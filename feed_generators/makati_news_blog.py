"""Makati City Government News feed.

The news page (https://www.makati.gov.ph/content/news) is an Angular app that
loads its stories from the public JSON API read here. The API returns each
story's full body, in which photos are embedded as base64 ``data:`` URIs of
several hundred kilobytes each rather than as files with an address. A feed
cannot point at them, so this feed carries the text only: no ``media:content``
and no images in ``content:encoded``.
"""

from datetime import datetime

import requests

from image_feeds import MANILA_TZ, clean_text, run_feed
from utils import DEFAULT_HEADERS, setup_logging

logger = setup_logging()

BLOG_URL = "https://www.makati.gov.ph/content/news"
FEED_NAME = "makati_news"
# First page of the endpoint behind the news list, nine stories per page.
API_URL = "https://www.makati.gov.ph/api/News/UnpinPaginatedNews/1/9"
STORY_URL = "https://www.makati.gov.ph/content/news/{}"
LOGO_URL = "https://www.makati.gov.ph/assets/images/branding/makati-logo.png"
SUMMARY_LENGTH = 300


def fetch_articles():
    """Fetch the newest stories from the news API."""
    response = requests.get(API_URL, headers=DEFAULT_HEADERS, timeout=120)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise ValueError(f"Unexpected API response: {str(payload)[:200]}")
    return parse_articles(payload)


def _story_date(item):
    """Use the date the site shows, with the publish time when it falls on that day."""
    shown = datetime.fromisoformat(item["datespecified"])
    posted = datetime.fromisoformat(item["threadTimestamp"]) if item.get("threadTimestamp") else shown
    return MANILA_TZ.localize(posted if posted.date() == shown.date() else shown)


def _summary(body_html, title):
    """Open the story text, which usually repeats the headline first."""
    text = clean_text(body_html)
    if text.lower().startswith(title.lower()):
        text = text[len(title) :].lstrip(" -\u2013\u2014:")
    if len(text) <= SUMMARY_LENGTH:
        return text
    return text[:SUMMARY_LENGTH].rsplit(" ", 1)[0] + "..."


def parse_articles(items):
    """Convert API items to feed entries."""
    articles = []
    seen = set()
    for item in items:
        try:
            link = STORY_URL.format(int(item["threadId"]))
            title = " ".join(item["threadTitle"].split())
            if not title or link in seen:
                continue
            articles.append(
                {
                    "link": link,
                    "title": title,
                    "description": _summary(item.get("threadContent") or "", title),
                    "date": _story_date(item),
                }
            )
            seen.add(link)
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.warning(f"Skipping malformed story: {e}")
    logger.info(f"Parsed {len(articles)} articles")
    return articles


if __name__ == "__main__":
    run_feed(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Makati City Government News",
        description="News from the Makati City Government",
        author="Makati City Government",
        logo_url=LOGO_URL,
        fetch_articles=fetch_articles,
    )
