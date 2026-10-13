"""Marikina City Government News feed.

The news page (https://marikina.gov.ph/news) is a shell that loads its posts
with the same ``fetch_news_side`` request made here. The request needs the
session cookie and the anti-forgery token every visitor gets from the page, so
both are read from the page first. The list reports each post's date, summary
and cover photo, and each new post's page is fetched for further photos.
"""

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from image_feeds import clean_text, collect_images, manila_date, run_feed
from utils import DEFAULT_HEADERS, setup_logging

logger = setup_logging()

BLOG_URL = "https://marikina.gov.ph/news"
FEED_NAME = "marikina_news"
LIST_URL = "https://marikina.gov.ph/fetch_news_side"
LOGO_URL = "https://marikina.gov.ph/images/MarikinaIco.ico"
DATE_PREFIX = "Post Date :"
DATE_FORMAT = "%m-%d-%Y"
# Shown for posts that were published without a photo.
PLACEHOLDER_IMAGE = "news-template.png"


def fetch_listing():
    """Load the news page for its session, then request the post list as the page does."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    page = session.get(BLOG_URL, timeout=30)
    page.raise_for_status()
    token = BeautifulSoup(page.text, "html.parser").find("meta", attrs={"name": "csrf-token"})
    if not token or not token.get("content"):
        raise ValueError("News page has no csrf-token")
    response = session.post(LIST_URL, data={"idfam": ""}, headers={"X-CSRF-TOKEN": token["content"]}, timeout=30)
    response.raise_for_status()
    return response.text


def _photo(url):
    return PLACEHOLDER_IMAGE not in url


def parse_listing(html):
    """Return the posts in the list the news page loads."""
    articles = []
    seen = set()
    for row in BeautifulSoup(html, "html.parser").find_all("tr"):
        try:
            title_link = row.select_one("a.post_views")
            link = urljoin(BLOG_URL, title_link["href"])
            if link in seen:
                continue
            summary = row.select_one("p.text-content")
            for more in summary.find_all("a"):
                more.decompose()
            date_text = row.select_one(".review-text").get_text().replace(DATE_PREFIX, "")
            covers = collect_images(row.find_all("img"), _photo, BLOG_URL)
            articles.append(
                {
                    "link": link,
                    "title": clean_text(str(title_link)),
                    "description": clean_text(str(summary)),
                    "date": manila_date(date_text, DATE_FORMAT),
                    "image_url": covers[0]["url"] if covers else "",
                }
            )
            seen.add(link)
        except (AttributeError, KeyError, TypeError, ValueError) as e:
            logger.warning(f"Skipping malformed post row: {e}")
    logger.info(f"Parsed {len(articles)} articles")
    return articles


def read_article(session, post):
    """Return ``(cover_url, body_images)`` of a post page."""
    response = session.get(post["link"], timeout=30)
    response.raise_for_status()
    # The page's other column holds links to city services.
    images = collect_images(BeautifulSoup(response.text, "html.parser").select(".col-md-8 img"), _photo, post["link"])
    return post.get("image_url") or (images[0]["url"] if images else ""), images


if __name__ == "__main__":
    run_feed(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Marikina City Government News",
        description="News and updates from the Marikina City Government",
        author="Marikina City Government",
        logo_url=LOGO_URL,
        fetch_articles=lambda: parse_listing(fetch_listing()),
        read_article=read_article,
    )
