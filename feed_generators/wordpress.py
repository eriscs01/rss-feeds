"""Shared generator for city government sites that run on WordPress.

WordPress publishes a native RSS feed per category (and per custom post type)
that lists the same posts as the site's listing page with exact publish times,
but its items carry no cover image. Each feed built here reads that native feed
for the post list, then takes the cover photo from the post's page and the
inline photos from the post body, and lays them out for ``content:encoded``.
"""

import json
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from image_feeds import clean_text, collect_images, plain_letters, run_feed
from native_rss import parse_rss
from utils import fetch_page, setup_logging

logger = setup_logging()

CONTENT_TAG = "{http://purl.org/rss/1.0/modules/content/}encoded"
# schema.org types that describe the post itself rather than the site or its author.
ARTICLE_TYPES = {"Article", "BlogPosting", "NewsArticle"}


@dataclass(frozen=True)
class WordPressSite:
    """How one WordPress site exposes the images of its posts."""

    author: str
    logo_url: str
    # Post photos live under these paths; body text also carries emoji images from other hosts.
    upload_paths: tuple[str, ...] = ("/wp-content/uploads/",)
    # Selector of the post photos on the post page, for sites whose native feed
    # has no post body. Without it the photos are read from the feed itself.
    body_selector: str | None = None
    # Whether post pages name a cover image. When they do not, no page is fetched.
    cover_on_page: bool = True
    # Use the first post photo as the cover of posts without one.
    first_image_as_cover: bool = True
    # Sitewide share images that some themes report for posts without a cover.
    placeholder_covers: tuple[str, ...] = ()
    # Strip markup, entities and the "The post ... appeared first on" line from feed excerpts.
    clean_excerpts: bool = True
    # Text of the link to the post that the theme appends to each feed excerpt.
    excerpt_more: str = ""

    def is_upload(self, url):
        return any(path in url for path in self.upload_paths)


def fetch_articles(feed_url, site):
    """Fetch the newest posts listed by a native WordPress RSS feed."""
    # Some sites emit whitespace before the XML declaration, which the parser rejects.
    xml = fetch_page(feed_url).lstrip()
    articles = []
    seen = set()
    for item, post in zip(ET.fromstring(xml).findall("channel/item"), parse_rss(xml), strict=True):
        # Some feeds append utm_* tracking parameters to every link.
        link = urlunsplit(urlsplit(item.findtext("link").strip())._replace(query="", fragment=""))
        if link in seen:
            continue
        seen.add(link)
        article = {
            "link": link,
            "title": plain_letters(post["title"]),
            "description": _clean_excerpt(post["description"], site) if site.clean_excerpts else post["description"],
            "date": post["date"],
            "categories": post["categories"],
        }
        if not site.body_selector:
            body = BeautifulSoup(item.findtext(CONTENT_TAG) or "", "html.parser")
            article["body_images"] = collect_images(body.find_all("img"), site.is_upload)
            if not site.cover_on_page:
                article["image_url"] = _first_image(article["body_images"], site)
        articles.append(article)
    logger.info(f"Parsed {len(articles)} articles")
    return articles


def _clean_excerpt(description, site):
    soup = BeautifulSoup(description, "html.parser")
    if site.excerpt_more:
        for more in soup.find_all("a"):
            if more.get_text(strip=True) == site.excerpt_more:
                more.decompose()
    for paragraph in soup.find_all("p"):
        if paragraph.find("a") and paragraph.get_text().startswith("The post "):
            paragraph.decompose()
    return plain_letters(clean_text(str(soup)))


def _page_cover(soup):
    """Return the cover image a post page names in its Open Graph or schema.org metadata."""
    og_image = soup.find("meta", property="og:image")
    cover_url = (og_image.get("content") or "").strip() if og_image else ""
    if cover_url:
        return cover_url
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except ValueError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in nodes:
            if not isinstance(node, dict):
                continue
            types = node.get("@type")
            image = node.get("image")
            if ARTICLE_TYPES.intersection(types if isinstance(types, list) else [types]) and isinstance(image, dict):
                url = image.get("url") or ""
                if url:
                    return url.strip()
    return ""


def parse_article_page(html, site):
    """Return ``(cover_url, body_images)`` of a post page.

    ``body_images`` is a list of ``{"url", "caption"}`` dicts, empty unless the
    site reads its post photos from the page.
    """
    soup = BeautifulSoup(html, "html.parser")
    cover_url = _page_cover(soup)
    if cover_url in site.placeholder_covers:
        cover_url = ""
    images = collect_images(soup.select(site.body_selector), site.is_upload) if site.body_selector else []
    return cover_url, images


def _first_image(images, site):
    return images[0]["url"] if images and site.first_image_as_cover else ""


def _read_article(site):
    def read_article(session, post):
        response = session.get(post["link"], timeout=30)
        response.raise_for_status()
        cover_url, images = parse_article_page(response.text, site)
        if not site.body_selector:
            images = post.get("body_images") or []
        return cover_url or _first_image(images, site), images

    return read_article


def run(feed_name, blog_url, title, description, feed_url, site):
    """Refresh one feed from the native RSS feed at ``feed_url``."""
    return run_feed(
        feed_name=feed_name,
        blog_url=blog_url,
        title=title,
        description=description,
        author=site.author,
        logo_url=site.logo_url,
        fetch_articles=lambda: fetch_articles(feed_url, site),
        read_article=_read_article(site) if site.cover_on_page else None,
    )
