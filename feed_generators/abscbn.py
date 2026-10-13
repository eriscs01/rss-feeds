"""Shared image enrichment for the ABS-CBN section feeds.

The section listing API only reports each article's cover image. The photos
inside an article, with their captions, live in the ``body_html`` that the
article page embeds in ``__NEXT_DATA__``. Each ``abscbn_*_blog.py`` script
calls ``enrich_posts`` to turn those into an HTML block for ``content:encoded``.
"""

import json
import re
from html import escape

import requests
from bs4 import BeautifulSoup
from lxml import etree

from utils import DEFAULT_HEADERS, get_feeds_dir, setup_logging, sort_posts_for_feed

logger = setup_logging()

CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"
NEXT_DATA_RE = re.compile(r'id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)
# Article pages fetched per run. The hourly listing rarely has more new articles than this.
MAX_FETCHES = 60


def _find_body_html(value):
    """Return the first ``body_html`` found in the page's nested module data."""
    if isinstance(value, dict):
        if isinstance(value.get("body_html"), str):
            return value["body_html"]
        value = list(value.values())
    if isinstance(value, list):
        for nested in value:
            found = _find_body_html(nested)
            if found is not None:
                return found
    return None


def parse_article_page(html):
    """Extract the cover caption and the body images from an article page.

    Returns ``(cover_caption, body_images, body_opens_with_image)`` where
    ``body_images`` is a list of ``{"url", "caption"}`` dicts.
    """
    match = NEXT_DATA_RE.search(html)
    if not match:
        raise ValueError("__NEXT_DATA__ not found in article page")
    page_props = json.loads(match.group(1))["props"]["pageProps"]

    thumbnail = ((page_props.get("content") or {}).get("associations") or {}).get("Thumbnail") or {}
    cover_caption = (thumbnail.get("description_text") or "").strip()
    if cover_caption == "-":
        cover_caption = ""

    body_html = _find_body_html(page_props.get("dataStr")) or ""
    images = []
    seen = set()
    for img in BeautifulSoup(body_html, "html.parser").find_all("img"):
        url = (img.get("src") or "").strip()
        if not url.startswith("https://") or url in seen:
            continue
        seen.add(url)
        wrapper = img.find_parent(class_="fr-img-caption")
        caption = wrapper.find(class_="fr-inner") if wrapper else None
        text = caption.get_text(" ", strip=True) if caption else (img.get("alt") or "").strip()
        images.append({"url": url, "caption": text})

    # Editors often repeat the cover photo as the first thing in the body.
    lead = body_html.split("<img", 1)[0]
    opens_with_image = bool(images) and not BeautifulSoup(lead, "html.parser").get_text(strip=True)
    return cover_caption, images, opens_with_image


def _figure(url, caption):
    figcaption = f"<figcaption>{escape(caption)}</figcaption>" if caption else ""
    return f'<figure><img src="{escape(url, quote=True)}" alt="{escape(caption, quote=True)}"/>{figcaption}</figure>'


def build_content_html(post, cover_caption, images, opens_with_image):
    """Lay out the lead image, the abstract, then the remaining article images."""
    images = list(images)
    if opens_with_image:
        lead = images.pop(0)
    elif post.get("image_url"):
        lead = {"url": post["image_url"], "caption": cover_caption}
    else:
        lead = None

    parts = []
    if lead:
        parts.append(_figure(lead["url"], lead["caption"]))
    if post.get("description"):
        parts.append(f"<p>{escape(post['description'])}</p>")
    parts.extend(_figure(image["url"], image["caption"]) for image in images)
    return "".join(parts)


def load_published_content(feed_name):
    """Map article links to the content already published in the feed XML.

    The cache directory is not persisted between scheduled runs, so the
    published feed is what keeps us from refetching every article each hour.
    """
    feed_file = get_feeds_dir() / f"feed_{feed_name}.xml"
    if not feed_file.exists():
        return {}
    try:
        root = etree.parse(str(feed_file)).getroot()
    except (etree.XMLSyntaxError, OSError) as e:
        logger.warning(f"Could not read {feed_file.name} for published content: {e}")
        return {}
    published = {}
    for item in root.iterfind("channel/item"):
        link = item.findtext("link")
        content = item.findtext(f"{{{CONTENT_NS}}}encoded")
        if link and content:
            published[link] = content
    return published


def merge_articles(new_articles, cached_posts):
    """Merge new articles into the cached ones, one per URL, sorted for feedgen.

    The listing API can return the same article under two IDs. Its URL is the
    feed item's link and GUID, so that is what has to be unique.
    """
    merged = {}
    for post in cached_posts:
        merged.setdefault(post["url"], post)
    added_count = 0
    for article in new_articles:
        if article["url"] not in merged:
            merged[article["url"]] = article
            added_count += 1

    logger.info(f"Added {added_count} new articles to cache")
    return sort_posts_for_feed(list(merged.values()), date_field="date")


def enrich_posts(posts, feed_name, max_fetches=MAX_FETCHES):
    """Set ``content_html`` on each post, fetching article pages only for new ones.

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
        if post["url"] in published:
            post["content_html"] = published[post["url"]]
            continue
        if fetched >= max_fetches:
            continue
        fetched += 1
        try:
            response = session.get(post["url"], timeout=30)
            response.raise_for_status()
            post["content_html"] = build_content_html(post, *parse_article_page(response.text))
        except (requests.RequestException, ValueError, KeyError, TypeError) as e:
            logger.warning(f"Could not read article images for {post['url']}: {e}")
    logger.info(f"Fetched {fetched} article pages for images")
    return posts
