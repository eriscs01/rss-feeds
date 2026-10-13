"""Shared pieces of the feeds that embed article images.

Every feed built here has the same layout: the cover image goes into
``media:content``, and ``content:encoded`` carries the cover, the summary, then
the remaining article images. Each site module only says where its posts come
from (``fetch_articles``) and, when the listing does not report them, how to
read the images of one article (``read_article``).
"""

import argparse
import re
from datetime import datetime
from html import escape
from urllib.parse import urljoin

import pytz
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

from abscbn import load_published_content
from feed_history import load_feed_history, require_posts
from utils import (
    DEFAULT_HEADERS,
    load_cache,
    merge_entries,
    save_cache,
    save_rss_feed,
    setup_feed_links,
    setup_logging,
)

logger = setup_logging()

# WordPress serves resized copies as <name>-<width>x<height>.<ext>.
SIZE_SUFFIX_RE = re.compile(r"-\d+x\d+(?=\.\w+$)")
# Newest entries kept in the cache and feed, so hourly runs do not grow them forever.
MAX_ENTRIES = 200
# Article pages fetched per run.
MAX_FETCHES = 30
# City sites report dates in Philippine time without an offset.
MANILA_TZ = pytz.timezone("Asia/Manila")


def manila_date(text, date_format):
    """Parse a date the site shows in Philippine time."""
    return MANILA_TZ.localize(datetime.strptime(" ".join(text.split()), date_format))


def original_image(url):
    """Identify an upload regardless of which resized copy a URL points at."""
    return SIZE_SUFFIX_RE.sub("", url)


def clean_text(html):
    """Reduce an HTML fragment to one line of plain text."""
    return " ".join(BeautifulSoup(html or "", "html.parser").get_text(" ").split())


def collect_images(imgs, accept=None, base_url=None):
    """Return the ``{"url", "caption"}`` of each distinct photo among ``imgs``.

    ``accept`` filters URLs (body text also carries emoji and theme images) and
    ``base_url`` resolves the relative ones.
    """
    images = []
    seen = set()
    for img in imgs:
        url = (img.get("src") or "").strip()
        if base_url and url and not url.startswith("data:"):
            url = urljoin(base_url, url)
        if not url.startswith("https://") or (accept and not accept(url)) or original_image(url) in seen:
            continue
        seen.add(original_image(url))
        figure = img.find_parent("figure")
        caption = figure.find("figcaption") if figure else None
        text = caption.get_text(" ", strip=True) if caption else (img.get("alt") or "").strip()
        images.append({"url": url, "caption": text})
    return images


def _figure(url, caption):
    figcaption = f"<figcaption>{escape(caption)}</figcaption>" if caption else ""
    return f'<figure><img src="{escape(url, quote=True)}" alt="{escape(caption, quote=True)}"/>{figcaption}</figure>'


def build_content_html(post, images):
    """Lay out the cover image, the summary, then the remaining post images."""
    cover_url = post.get("image_url")
    cover_key = original_image(cover_url) if cover_url else None
    # Editors usually repeat the cover photo in the body, where it may carry a caption.
    cover_caption = next((image["caption"] for image in images if original_image(image["url"]) == cover_key), "")
    parts = []
    if cover_url:
        parts.append(_figure(cover_url, cover_caption))
    if post.get("description"):
        parts.append(f"<p>{escape(post['description'])}</p>")
    parts.extend(
        _figure(image["url"], image["caption"]) for image in images if original_image(image["url"]) != cover_key
    )
    return "".join(parts)


def enrich_posts(posts, feed_name, read_article=None, max_fetches=MAX_FETCHES):
    """Set ``image_url`` and ``content_html`` on each post, reading articles only for new ones.

    ``read_article(session, post)`` returns ``(cover_url, body_images)``. Without
    it, the cover and the ``body_images`` the listing reported are used as they are.
    Posts whose article cannot be read are left without ``content_html`` so the
    next run tries them again.
    """
    published = load_published_content(feed_name)
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    fetched = 0
    # Posts are sorted oldest-first for feedgen, so walk them newest-first.
    for post in reversed(posts):
        if post.get("content_html"):
            post.pop("body_images", None)
            continue
        if post["link"] in published:
            post["content_html"] = published[post["link"]]
            post.pop("body_images", None)
            if not post.get("image_url"):
                # Published content opens with the cover image when the post has one.
                first_image = BeautifulSoup(post["content_html"], "html.parser").find("img")
                post["image_url"] = first_image.get("src", "") if first_image else ""
            continue
        if read_article is None:
            post["content_html"] = build_content_html(post, post.pop("body_images", None) or [])
            continue
        if fetched >= max_fetches:
            continue
        fetched += 1
        try:
            post["image_url"], images = read_article(session, post)
            post["content_html"] = build_content_html(post, images)
            post.pop("body_images", None)
        except (requests.RequestException, ValueError, KeyError, TypeError) as e:
            logger.warning(f"Could not read article images for {post['link']}: {e}")
    logger.info(f"Fetched {fetched} article pages for images")
    return posts


def generate_rss_feed(posts, feed_name, blog_url, title, description, author, logo_url):
    fg = FeedGenerator()
    fg.load_extension("media")
    fg.title(title)
    fg.description(description)
    fg.language("en")
    fg.author({"name": author})
    fg.logo(logo_url)
    setup_feed_links(fg, blog_url=blog_url, feed_name=feed_name)

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.description(post.get("description") or post["title"])
        if post.get("content_html"):
            fe.content(post["content_html"], type="CDATA")
        fe.link(href=post["link"])
        fe.id(post["link"])
        fe.published(post["date"])
        fe.updated(post["date"])
        if post.get("image_url"):
            fe.media.content({"url": post["image_url"], "medium": "image"})
        for category in post.get("categories", []):
            fe.category(term=category)

    logger.info(f"Generated RSS feed with {len(posts)} entries")
    return fg


def run_feed(
    feed_name,
    blog_url,
    title,
    description,
    author,
    logo_url,
    fetch_articles,
    read_article=None,
    max_fetches=MAX_FETCHES,
):
    """Refresh one feed: fetch, merge with the cache, add images, write the XML."""
    argparse.ArgumentParser(description=f"Generate {title} RSS feed").parse_args()
    cache = load_cache(feed_name)
    new_articles = require_posts(fetch_articles())
    for article in new_articles:
        # A listing without a cover must not erase the one found earlier on the article page.
        if not article.get("image_url"):
            article.pop("image_url", None)
    # merge_entries sorts oldest-first (feedgen reverses), so the newest are at the end.
    # Listings show only their newest posts and scheduled runs do not persist the
    # cache, so the published feed is what keeps older posts in the output.
    known = merge_entries(cache.get("entries", []), load_feed_history(feed_name))
    posts = merge_entries(new_articles, known)[-MAX_ENTRIES:]
    enrich_posts(posts, feed_name, read_article, max_fetches)
    save_cache(feed_name, posts)
    save_rss_feed(generate_rss_feed(posts, feed_name, blog_url, title, description, author, logo_url), feed_name)
    logger.info("Done!")
    return True
