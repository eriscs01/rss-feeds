"""Pasig City Government News and Releases feed.

The listing page (https://pasigcity.gov.ph/news-and-releases) is server-rendered
and shows the 30 newest posts with their date, summary and cover photo. Each new
post's page is fetched for its inline photos.

The server sends its certificate without the intermediate that issued it.
Browsers fetch the missing one themselves, but Python does not, so the public
Sectigo intermediate is kept in ``certs/`` and added to the trusted roots:
the chain is still verified in full.
"""

import atexit
import os
import tempfile
from pathlib import Path

import certifi
import requests
from bs4 import BeautifulSoup

from image_feeds import clean_text, collect_images, manila_date, run_feed
from utils import DEFAULT_HEADERS, setup_logging

logger = setup_logging()

BLOG_URL = "https://pasigcity.gov.ph/news-and-releases"
FEED_NAME = "pasig_news"
LOGO_URL = "https://pasigcity.gov.ph/img/favicon.ico"
DATE_FORMAT = "%B %d, %Y"
INTERMEDIATE_CERT = Path(__file__).parent / "certs" / "sectigo_public_server_authentication_ca_dv_r36.pem"


def make_ca_bundle():
    """Write certifi's roots plus the missing intermediate to a file ``requests`` can verify against."""
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as bundle:
        bundle.write(Path(certifi.where()).read_text() + "\n" + INTERMEDIATE_CERT.read_text())
    atexit.register(os.unlink, bundle.name)
    return bundle.name


def fetch_listing(ca_bundle):
    response = requests.get(BLOG_URL, headers=DEFAULT_HEADERS, timeout=30, verify=ca_bundle)
    response.raise_for_status()
    return response.text


def parse_listing(html):
    """Return the posts shown on the listing page."""
    articles = []
    seen = set()
    for card in BeautifulSoup(html, "html.parser").select(".news-content"):
        try:
            link = card.find("a", href=True)["href"].strip()
            if link in seen:
                continue
            image = card.find("img")
            # The card's last paragraph is the summary; the first one is the date.
            summary = card.find_all("p")[-1]
            articles.append(
                {
                    "link": link,
                    "title": clean_text(str(card.find("h4"))),
                    "description": "" if "date" in (summary.get("class") or []) else clean_text(str(summary)),
                    "date": manila_date(card.select_one("p.date").get_text(), DATE_FORMAT),
                    "image_url": (image.get("src") or "").strip() if image else "",
                }
            )
            seen.add(link)
        except (AttributeError, KeyError, TypeError, ValueError, IndexError) as e:
            logger.warning(f"Skipping malformed post card: {e}")
    logger.info(f"Parsed {len(articles)} articles")
    return articles


def parse_article_page(html, post):
    """Return ``(cover_url, body_images)`` of a post page."""
    soup = BeautifulSoup(html, "html.parser")
    cover = soup.select_one(".newspage-image img")
    cover_url = (cover.get("src") or "").strip() if cover else ""
    # The right-hand column of the same section lists other posts.
    images = collect_images(soup.select("section.newspage-content .col-lg-9 img"), base_url=post["link"])
    return cover_url or post.get("image_url", ""), images


def main():
    ca_bundle = make_ca_bundle()

    def read_article(session, post):
        response = session.get(post["link"], timeout=30, verify=ca_bundle)
        response.raise_for_status()
        return parse_article_page(response.text, post)

    run_feed(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Pasig City Government News and Releases",
        description="News and releases from the Pasig City Government",
        author="Pasig City Government",
        logo_url=LOGO_URL,
        fetch_articles=lambda: parse_listing(fetch_listing(ca_bundle)),
        read_article=read_article,
    )


if __name__ == "__main__":
    main()
