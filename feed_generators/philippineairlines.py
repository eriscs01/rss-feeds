"""Shared generator for the Philippine Airlines News & Events feeds.

The listing page (https://www.philippineairlines.com/ph/en/newsevent-listingpage.html)
is an Adobe Experience Manager page whose cards are drawn by JavaScript. AEM
publishes the same content as JSON at ``<page>.model.json``: one tab per section
("Travel Advisory", "Press releases statements"), each holding a carousel of
cards with the title, summary, date and link of every post in that section.
Each ``philippineairlines_*_blog.py`` script reads one tab of that JSON.

The cards carry no photos and the post pages only repeat a generic banner, so
the feeds carry the text only, like the Makati feed.
"""

import json
from urllib.parse import urljoin

from image_feeds import manila_date, run_feed
from static_pages import fetch_page
from utils import setup_logging

logger = setup_logging()

BLOG_URL = "https://www.philippineairlines.com/ph/en/newsevent-listingpage.html"
MODEL_URL = "https://www.philippineairlines.com/ph/en/newsevent-listingpage.model.json"
LOGO_URL = "https://s7ap1.scene7.com/is/image/palprod/apple-touch-icon"
AUTHOR = "Philippine Airlines"
# Cards show dates such as "12 October 2026", in Philippine time.
DATE_FORMAT = "%d %B %Y"


def _items(component, *path):
    """Follow ``:items`` children of an AEM model component by name."""
    for name in path:
        component = component[":items"][name]
    return component


def find_cards(model, section):
    """Return the cards of the tab whose experience fragment path ends in ``/section``.

    Tabs are matched by their fragment path rather than their generated item ids,
    which change whenever an editor recreates a tab.
    """
    tabs = _items(model, "root", "mid-responsivegrid", "customtabs")
    for name in tabs[":itemsOrder"]:
        fragment = tabs[":items"][name]
        path = fragment.get("localizedFragmentVariationPath", "").removesuffix("/jcr:content")
        if path.rsplit("/", 1)[-1] == section:
            carousel = _items(fragment, "root", "customcarousel")
            return [carousel[":items"][card] for card in carousel[":itemsOrder"]]
    raise ValueError(f"Listing has no {section!r} tab")


def parse_cards(cards):
    """Convert AEM cards to feed entries."""
    articles = []
    seen = set()
    for card in cards:
        try:
            link = urljoin(BLOG_URL, card["ctaDetails"]["item0"]["linkUrl"].strip())
            title = " ".join(card["common"]["primary"].split())
            if not title or link in seen:
                continue
            articles.append(
                {
                    "link": link,
                    "title": title,
                    "description": " ".join((card["common"].get("secondary") or "").split()),
                    "date": manila_date(card["cardDetails"]["tertiary"], DATE_FORMAT),
                }
            )
            seen.add(link)
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            logger.warning(f"Skipping malformed card: {e}")
    logger.info(f"Parsed {len(articles)} articles")
    return articles


def fetch_articles(section):
    """Fetch the listing model and return the posts of one section."""
    return parse_cards(find_cards(json.loads(fetch_page(MODEL_URL)), section))


def run(feed_name, blog_url, section, title, description):
    """Refresh the feed of the listing tab named ``section``."""
    return run_feed(
        feed_name=feed_name,
        blog_url=blog_url,
        title=title,
        description=description,
        author=AUTHOR,
        logo_url=LOGO_URL,
        fetch_articles=lambda: fetch_articles(section),
    )
