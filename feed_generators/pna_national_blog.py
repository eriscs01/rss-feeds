import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import pytz
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

from utils import get_cache_dir, get_feeds_dir, setup_feed_links, sort_posts_for_feed

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BLOG_URL = "https://www.pna.gov.ph/categories/national"
FEED_NAME = "pna_national"
PH_TZ = pytz.timezone("Asia/Manila")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_cache_file():
    return get_cache_dir() / "pna_national_posts.json"


def fetch_page(page_num=1):
    url = BLOG_URL if page_num == 1 else f"{BLOG_URL}?p={page_num}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def parse_articles(html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.find_all("div", class_="article-item")
    articles = []

    for item in items:
        # Title and URL
        h2 = item.find("h2")
        if not h2:
            continue
        title_link = h2.find("a")
        if not title_link:
            continue
        title = title_link.get_text(strip=True)
        url = title_link.get("href", "")
        if not url or "/articles/" not in url:
            continue

        # Article ID from URL
        match = re.search(r"/articles/(\d+)", url)
        if not match:
            continue
        article_id = match.group(1)

        # Thumbnail image
        img = item.find("img")
        image_url = img.get("src", "") if img else ""

        # Date (red paragraph)
        date_p = item.find("p", class_=lambda c: c and "text-red-600" in c)
        date_str = date_p.get_text(strip=True) if date_p else ""

        # Parse date: "March 5, 2026, 9:42 pm" (may have "Updated on..." appended)
        pub_date = None
        if date_str:
            # Extract just the first date occurrence: "Month D, YYYY, H:MM am/pm"
            date_match = re.search(r"([A-Za-z]+ \d{1,2}, \d{4}, \d{1,2}:\d{2} [aApP][mM])", date_str)
            if date_match:
                try:
                    naive = datetime.strptime(date_match.group(1), "%B %d, %Y, %I:%M %p")
                    pub_date = PH_TZ.localize(naive).isoformat()
                except ValueError:
                    logger.warning(f"Could not parse date: {date_match.group(1)!r}")
            else:
                logger.warning(f"No date pattern found in: {date_str!r}")

        # Description (non-red paragraph)
        description = ""
        for p in item.find_all("p"):
            classes = p.get("class", [])
            if "text-red-600" not in classes:
                text = p.get_text(strip=True)
                if text:
                    description = text
                    break

        articles.append({
            "id": article_id,
            "url": url,
            "title": title,
            "description": description,
            "date": pub_date,
            "image_url": image_url,
        })

    return articles


def get_max_page(html):
    soup = BeautifulSoup(html, "html.parser")
    page_links = soup.find_all("a", href=re.compile(r"\?p=\d+"))
    max_page = 1
    for link in page_links:
        m = re.search(r"\?p=(\d+)", link["href"])
        if m:
            max_page = max(max_page, int(m.group(1)))
    return max_page


def load_cache():
    cache_file = get_cache_file()
    if cache_file.exists():
        with open(cache_file, "r") as f:
            data = json.load(f)
            logger.info(f"Loaded cache with {len(data.get('posts', []))} posts")
            return data
    logger.info("No cache file found, starting fresh")
    return {"last_updated": None, "posts": []}


def save_cache(posts):
    cache_file = get_cache_file()
    data = {
        "last_updated": datetime.now(pytz.UTC).isoformat(),
        "posts": posts,
    }
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved cache with {len(posts)} posts to {cache_file}")


def merge_articles(new_articles, cached_posts):
    existing_ids = {p["id"] for p in cached_posts}
    merged = list(cached_posts)
    added = 0
    for article in new_articles:
        if article["id"] not in existing_ids:
            merged.append(article)
            existing_ids.add(article["id"])
            added += 1
    logger.info(f"Added {added} new articles to cache")
    return sort_posts_for_feed(merged, date_field="date")


def fetch_all_pages():
    logger.info("Fetching page 1...")
    html = fetch_page(1)
    articles = parse_articles(html)
    max_page = get_max_page(html)
    logger.info(f"Found {max_page} pages total")
    for page_num in range(2, max_page + 1):
        logger.info(f"Fetching page {page_num}/{max_page}...")
        try:
            page_html = fetch_page(page_num)
            articles.extend(parse_articles(page_html))
        except Exception as e:
            logger.warning(f"Failed to fetch page {page_num}: {e}")
            break
    logger.info(f"Fetched {len(articles)} total articles from {max_page} pages")
    return articles


def generate_rss_feed(posts):
    fg = FeedGenerator()
    fg.load_extension("media")
    fg.title("Philippine News Agency - National")
    fg.description(
        "Latest national news from the Philippine News Agency (PNA), the official newswire service of the Philippine government."
    )
    fg.language("en")
    fg.author({"name": "Philippine News Agency"})
    fg.logo("https://www.pna.gov.ph/favicon.ico")
    fg.subtitle("Official Philippine government news wire - National")
    setup_feed_links(fg, blog_url=BLOG_URL, feed_name=FEED_NAME)

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.description(post.get("description", ""))
        fe.link(href=post["url"])
        fe.id(post["url"])

        if post.get("image_url"):
            fe.media.content({"url": post["image_url"], "medium": "image"})

        if post.get("date"):
            try:
                dt = datetime.fromisoformat(post["date"])
                fe.published(dt)
                fe.updated(dt)
            except (ValueError, TypeError):
                pass

    logger.info(f"Generated RSS feed with {len(posts)} entries")
    return fg


def save_rss_feed(fg):
    feeds_dir = get_feeds_dir()
    output_file = feeds_dir / f"feed_{FEED_NAME}.xml"
    fg.rss_file(str(output_file), pretty=True)
    logger.info(f"Saved RSS feed to {output_file}")
    return output_file


def main(full=False):
    cache = load_cache()

    if full or not cache["posts"]:
        logger.info("Running full fetch across all pages")
        new_articles = fetch_all_pages()
    else:
        logger.info("Running incremental fetch (page 1 only)")
        html = fetch_page(1)
        new_articles = parse_articles(html)
        logger.info(f"Found {len(new_articles)} articles on page 1")

    posts = merge_articles(new_articles, cache["posts"])
    save_cache(posts)
    feed = generate_rss_feed(posts)
    save_rss_feed(feed)
    logger.info("Done!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PNA National RSS feed")
    parser.add_argument("--full", action="store_true", help="Fetch all pages (full reset)")
    args = parser.parse_args()
    main(full=args.full)
