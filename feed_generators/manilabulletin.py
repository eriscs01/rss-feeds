"""Shared generator for Manila Bulletin category feeds.

The category pages (https://mb.com.ph/category/<name>) sit behind a Cloudflare
browser challenge and mix several widgets, some of which show articles from
other categories. Their "Latest" widget is the only one scoped to the page's
own category, and it loads its articles from a public JSON API filtered by
section/subsection ID. Each ``manilabulletin_*_blog.py`` script reads that API
for its own category.

The listing only reports each article's cover image, without a caption. The
article API returns the full body, whose inline photos and captions are turned
into an HTML block for ``content:encoded``.
"""

import argparse
from datetime import datetime
from html import escape

import pytz
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

from abscbn import load_published_content
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

# Endpoint behind the "Latest" widget of every category page.
API_URL = "https://mb.com.ph/api/pb/fetch-articles-paginated"
API_LIMIT = 100
# The API reports publish_time in Philippine time without an offset.
MANILA_TZ = pytz.timezone("Asia/Manila")
PUBLISH_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
# Newest entries kept in the cache and feed, so hourly runs do not grow them forever.
MAX_ENTRIES = 200
# The site's other logo files are not publicly readable, which leaves readers without an icon.
LOGO_URL = "https://mb.com.ph/manilabulletin/uploads/global_files/favicon.png"
# Full article by its cms_article_id; article pages themselves sit behind the Cloudflare challenge.
ARTICLE_API_URL = "https://mb.com.ph/api/pb/article/{}"
# Articles fetched per run. The hourly listing rarely has more new articles than this.
MAX_FETCHES = 60


def fetch_articles(section_id, subsection_id=None, limit=API_LIMIT):
    """Fetch the newest articles of one section, or of one of its subsections."""
    params = {"limit": limit, "hide_widget_in_pagination": 1, "section_id": section_id}
    if subsection_id is not None:
        params["subsection_id"] = subsection_id
    response = requests.get(API_URL, params=params, headers=DEFAULT_HEADERS, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if payload.get("response") != "success" or not isinstance(payload.get("data"), list):
        raise ValueError(f"Unexpected API response: {str(payload)[:200]}")
    return parse_articles(payload["data"], section_id, subsection_id)


def parse_articles(items, section_id, subsection_id=None):
    """Convert API items to feed entries, skipping any outside the requested category."""
    articles = []
    seen = set()
    for item in items:
        try:
            link = item["link"]
            title = item["title"].strip()
            if not link or not title or link in seen:
                continue
            # The API ignores unknown IDs and returns the sitewide listing instead.
            if item.get("section_id") != section_id or (
                subsection_id is not None and item.get("sub_section_id") != subsection_id
            ):
                logger.warning(f"Skipping article outside the requested category: {link}")
                continue
            date = MANILA_TZ.localize(datetime.strptime(item["publish_time"], PUBLISH_TIME_FORMAT))
            image = item.get("image")
            articles.append(
                {
                    "link": link,
                    "article_id": item.get("cms_article_id"),
                    "title": title,
                    "description": (item.get("summary") or item.get("subtitle") or "").strip(),
                    "date": date,
                    "author": (item.get("byline") or item.get("author_name") or "").strip(),
                    "category": item.get("sub_section_name") or item.get("section_name") or "",
                    "image_url": image.get("full", "") if isinstance(image, dict) else "",
                }
            )
            seen.add(link)
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.warning(f"Skipping malformed article {item.get('link') if isinstance(item, dict) else item!r}: {e}")
    logger.info(f"Parsed {len(articles)} articles")
    return articles


def parse_body_images(body_html):
    """Return the ``{"url", "caption"}`` of each image inside an article body."""
    images = []
    seen = set()
    for img in BeautifulSoup(body_html, "html.parser").find_all("img"):
        url = (img.get("src") or "").strip()
        if not url.startswith("https://") or url in seen:
            continue
        seen.add(url)
        wrapper = img.find_parent(class_="body_image")
        caption = wrapper.find(class_="image-caption") if wrapper else None
        text = caption.get_text(" ", strip=True) if caption else (img.get("alt") or "").strip()
        images.append({"url": url, "caption": text})
    return images


def _figure(url, caption):
    figcaption = f"<figcaption>{escape(caption)}</figcaption>" if caption else ""
    return f'<figure><img src="{escape(url, quote=True)}" alt="{escape(caption, quote=True)}"/>{figcaption}</figure>'


def build_content_html(post, images):
    """Lay out the cover image, the summary, then the remaining article images."""
    cover_url = post.get("image_url")
    # Editors usually repeat the cover photo in the body, where it carries its caption.
    cover_caption = next((image["caption"] for image in images if image["url"] == cover_url), "")
    parts = []
    if cover_url:
        parts.append(_figure(cover_url, cover_caption))
    if post.get("description"):
        parts.append(f"<p>{escape(post['description'])}</p>")
    parts.extend(_figure(image["url"], image["caption"]) for image in images if image["url"] != cover_url)
    return "".join(parts)


def enrich_posts(posts, feed_name, max_fetches=MAX_FETCHES):
    """Set ``content_html`` on each post, fetching articles only for new ones.

    Posts whose article cannot be fetched are left without ``content_html`` so
    the next run tries them again.
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
            continue
        if not post.get("article_id") or fetched >= max_fetches:
            continue
        fetched += 1
        try:
            response = session.get(ARTICLE_API_URL.format(post["article_id"]), timeout=30)
            response.raise_for_status()
            data = response.json()["data"]
            # The API answers unknown IDs with some other article instead of an error.
            if data.get("link") != post["link"]:
                raise ValueError(f"article API returned {data.get('link')}")
            post["content_html"] = build_content_html(post, parse_body_images(data.get("body") or ""))
        except (requests.RequestException, ValueError, KeyError, TypeError) as e:
            logger.warning(f"Could not read article images for {post['link']}: {e}")
    logger.info(f"Fetched {fetched} articles for images")
    return posts


def generate_rss_feed(posts, feed_name, blog_url, title, description):
    fg = FeedGenerator()
    fg.load_extension("media")
    fg.title(title)
    fg.description(description)
    fg.language("en")
    fg.author({"name": "Manila Bulletin"})
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
        if post.get("author"):
            fe.author({"name": post["author"]})
        if post.get("category"):
            fe.category(term=post["category"])

    logger.info(f"Generated RSS feed with {len(posts)} entries")
    return fg


def run(feed_name, blog_url, title, description, section_id, subsection_id=None):
    """Refresh one category feed: fetch, merge with the cache, write the XML."""
    argparse.ArgumentParser(description=f"Generate {title} RSS feed").parse_args()
    cache = load_cache(feed_name)
    new_articles = fetch_articles(section_id, subsection_id)
    if not new_articles:
        raise ValueError(f"No articles returned for {blog_url}")
    # merge_entries sorts oldest-first (feedgen reverses), so the newest are at the end.
    posts = merge_entries(new_articles, cache.get("entries", []))[-MAX_ENTRIES:]
    enrich_posts(posts, feed_name)
    save_cache(feed_name, posts)
    save_rss_feed(generate_rss_feed(posts, feed_name, blog_url, title, description), feed_name)
    logger.info("Done!")
    return True
