"""Shared generator for the Quezon City Government news feeds.

Each News and Media listing page (https://quezoncity.gov.ph/news-and-media/<name>/)
shows the posts of one WordPress category. The site publishes a native RSS feed
per category that lists the same posts with exact publish times, but without
any images. Each ``quezoncity_*_blog.py`` script reads its category feed, then
fetches each new post's page for its cover photo and inline images and turns
them into an HTML block for ``content:encoded``.
"""

import argparse
import re
from html import escape
from urllib.parse import urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

from abscbn import load_published_content
from feed_history import load_feed_history
from native_rss import parse_rss
from utils import (
    DEFAULT_HEADERS,
    fetch_page,
    load_cache,
    merge_entries,
    save_cache,
    save_rss_feed,
    setup_feed_links,
    setup_logging,
)

logger = setup_logging()

CATEGORY_FEED_URL = "https://quezoncity.gov.ph/category/{}/feed/"
LOGO_URL = "https://quezoncity.gov.ph/wp-content/themes/qcproject/images/favicon.png"
# Post photos live here; body text also carries emoji images from other hosts.
UPLOADS_PATH = "/wp-content/uploads/"
# WordPress serves resized copies as <name>-<width>x<height>.<ext>.
SIZE_SUFFIX_RE = re.compile(r"-\d+x\d+(?=\.\w+$)")
# Newest entries kept in the cache and feed, so hourly runs do not grow them forever.
MAX_ENTRIES = 200
# Post pages fetched per run. The category feed lists 10 posts.
MAX_FETCHES = 30


def fetch_articles(category_slug):
    """Fetch the newest posts of one category from its native RSS feed."""
    articles = []
    seen = set()
    for post in parse_rss(fetch_page(CATEGORY_FEED_URL.format(category_slug))):
        # The feed appends utm_* tracking parameters to every link.
        link = urlunsplit(urlsplit(post["link"])._replace(query="", fragment=""))
        if link in seen:
            continue
        seen.add(link)
        articles.append(
            {
                "link": link,
                "title": post["title"],
                "description": post["description"],
                "date": post["date"],
                "categories": post["categories"],
            }
        )
    logger.info(f"Parsed {len(articles)} articles")
    return articles


def _original_image(url):
    """Identify an upload regardless of which resized copy a URL points at."""
    return SIZE_SUFFIX_RE.sub("", url)


def parse_article_page(html):
    """Return ``(cover_url, body_images)`` of a post page.

    ``body_images`` is a list of ``{"url", "caption"}`` dicts.
    """
    soup = BeautifulSoup(html, "html.parser")
    og_image = soup.find("meta", property="og:image")
    cover_url = (og_image.get("content") or "").strip() if og_image else ""

    images = []
    seen = set()
    for img in soup.select("article .single-post-inner img"):
        url = (img.get("src") or "").strip()
        if not url.startswith("https://") or UPLOADS_PATH not in url or _original_image(url) in seen:
            continue
        seen.add(_original_image(url))
        figure = img.find_parent("figure")
        caption = figure.find("figcaption") if figure else None
        text = caption.get_text(" ", strip=True) if caption else (img.get("alt") or "").strip()
        images.append({"url": url, "caption": text})
    return cover_url, images


def _figure(url, caption):
    figcaption = f"<figcaption>{escape(caption)}</figcaption>" if caption else ""
    return f'<figure><img src="{escape(url, quote=True)}" alt="{escape(caption, quote=True)}"/>{figcaption}</figure>'


def build_content_html(post, images):
    """Lay out the cover image, the summary, then the remaining post images."""
    cover_url = post.get("image_url")
    cover_key = _original_image(cover_url) if cover_url else None
    # Editors usually repeat the cover photo in the body, where it may carry a caption.
    cover_caption = next((image["caption"] for image in images if _original_image(image["url"]) == cover_key), "")
    parts = []
    if cover_url:
        parts.append(_figure(cover_url, cover_caption))
    if post.get("description"):
        parts.append(f"<p>{escape(post['description'])}</p>")
    parts.extend(
        _figure(image["url"], image["caption"]) for image in images if _original_image(image["url"]) != cover_key
    )
    return "".join(parts)


def enrich_posts(posts, feed_name, max_fetches=MAX_FETCHES):
    """Set ``image_url`` and ``content_html`` on each post, fetching pages only for new ones.

    Posts whose page cannot be fetched are left without ``content_html`` so the
    next run tries them again.
    """
    published = load_published_content(feed_name)
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    fetched = 0
    # Posts are sorted oldest-first for feedgen, so walk them newest-first.
    for post in reversed(posts):
        if post.get("content_html"):
            continue
        if post["link"] in published:
            post["content_html"] = published[post["link"]]
            if not post.get("image_url"):
                # Published content opens with the cover image when the post has one.
                first_image = BeautifulSoup(post["content_html"], "html.parser").find("img")
                post["image_url"] = first_image.get("src", "") if first_image else ""
            continue
        if fetched >= max_fetches:
            continue
        fetched += 1
        try:
            response = session.get(post["link"], timeout=30)
            response.raise_for_status()
            post["image_url"], images = parse_article_page(response.text)
            post["content_html"] = build_content_html(post, images)
        except (requests.RequestException, ValueError, KeyError, TypeError) as e:
            logger.warning(f"Could not read article images for {post['link']}: {e}")
    logger.info(f"Fetched {fetched} article pages for images")
    return posts


def generate_rss_feed(posts, feed_name, blog_url, title, description):
    fg = FeedGenerator()
    fg.load_extension("media")
    fg.title(title)
    fg.description(description)
    fg.language("en")
    fg.author({"name": "Quezon City Government"})
    fg.logo(LOGO_URL)
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


def run(feed_name, blog_url, title, description, category_slug):
    """Refresh one category feed: fetch, merge with the cache, write the XML."""
    argparse.ArgumentParser(description=f"Generate {title} RSS feed").parse_args()
    cache = load_cache(feed_name)
    new_articles = fetch_articles(category_slug)
    # merge_entries sorts oldest-first (feedgen reverses), so the newest are at the end.
    # The category feed lists only 10 posts and scheduled runs do not persist the
    # cache, so the published feed is what keeps older posts in the output.
    known = merge_entries(cache.get("entries", []), load_feed_history(feed_name))
    posts = merge_entries(new_articles, known)[-MAX_ENTRIES:]
    enrich_posts(posts, feed_name)
    save_cache(feed_name, posts)
    save_rss_feed(generate_rss_feed(posts, feed_name, blog_url, title, description), feed_name)
    logger.info("Done!")
    return True
