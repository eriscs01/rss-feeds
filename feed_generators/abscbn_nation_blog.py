import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import pytz
import requests
from feedgen.feed import FeedGenerator

from utils import setup_feed_links, sort_posts_for_feed

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BLOG_URL = "https://www.abs-cbn.com/news/nation"
FEED_NAME = "abscbn_nation"
IMAGE_BASE_URL = "https://od2-image-api.abs-cbn.com/prod"


def get_project_root():
    return Path(__file__).parent.parent


def get_cache_file():
    return get_project_root() / "cache" / "abscbn_nation_posts.json"


def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def parse_articles(html):
    """Extract articles from __NEXT_DATA__ JSON embedded in the page."""
    match = re.search(
        r'id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL
    )
    if not match:
        logger.warning("__NEXT_DATA__ not found in page")
        return []

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse __NEXT_DATA__ JSON: {e}")
        return []

    try:
        content = data["props"]["pageProps"]["content"]
        list_items = content.get("listItem", [])
    except (KeyError, TypeError) as e:
        logger.error(f"Unexpected data structure: {e}")
        return []

    articles = []
    for item in list_items:
        article_id = item.get("articleId") or item.get("_id", "")
        if not article_id:
            continue

        title = item.get("title") or item.get("slugline", "")
        if not title:
            continue

        slugline_url = item.get("slugline_url", "")
        url = f"https://www.abs-cbn.com/{slugline_url}" if slugline_url else ""
        if not url:
            continue

        author = item.get("penName") or item.get("author", "")
        abstract = item.get("abstract", "")
        date = item.get("createdDateFull", "")
        category = item.get("category", "")
        tags = item.get("tags", "")

        image_path = item.get("largeUrl") or item.get("coverImage") or item.get("image", "")
        image_url = f"{IMAGE_BASE_URL}/{image_path}" if image_path else ""
        image_mime = item.get("mimetype", "image/jpeg") if image_path else ""

        articles.append({
            "id": article_id,
            "url": url,
            "title": title,
            "description": abstract,
            "date": date,
            "author": author,
            "category": category,
            "tags": tags,
            "image_url": image_url,
            "image_mime": image_mime,
        })

    logger.info(f"Parsed {len(articles)} articles from page")
    return articles


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
    cache_file.parent.mkdir(exist_ok=True)
    data = {
        "last_updated": datetime.now(pytz.UTC).isoformat(),
        "posts": posts,
    }
    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved cache with {len(posts)} posts to {cache_file}")


def merge_articles(new_articles, cached_posts):
    """Merge new articles into cache, dedup by article ID, sort by date desc."""
    existing_ids = {p["id"] for p in cached_posts}
    merged = list(cached_posts)

    added_count = 0
    for article in new_articles:
        if article["id"] not in existing_ids:
            merged.append(article)
            existing_ids.add(article["id"])
            added_count += 1

    logger.info(f"Added {added_count} new articles to cache")
    return sort_posts_for_feed(merged, date_field="date")


def generate_rss_feed(posts):
    fg = FeedGenerator()
    fg.title("ABS-CBN News Nation")
    fg.description(
        "Get the latest national news, covering politics, society, and current events in the Philippines."
    )
    fg.language("en")
    fg.author({"name": "ABS-CBN News"})
    fg.logo("https://od2-image-api.abs-cbn.com/prod/newsfavicon.webp")
    fg.subtitle("Latest national news from ABS-CBN")
    setup_feed_links(fg, blog_url=BLOG_URL, feed_name=FEED_NAME)

    for post in posts:
        fe = fg.add_entry()
        fe.title(post["title"])
        fe.description(post["description"])
        fe.link(href=post["url"])

        if post.get("image_url"):
            fe.enclosure(url=post["image_url"], length="0", type=post.get("image_mime", "image/jpeg"))
        fe.id(post["url"])

        if post.get("date"):
            try:
                dt = datetime.fromisoformat(post["date"].replace("Z", "+00:00"))
                fe.published(dt)
                fe.updated(dt)
            except (ValueError, TypeError):
                pass

        if post.get("author"):
            fe.author({"name": post["author"]})

        if post.get("category"):
            fe.category(term=post["category"])

    logger.info(f"Generated RSS feed with {len(posts)} entries")
    return fg


def save_rss_feed(feed_generator):
    feeds_dir = get_project_root() / "feeds"
    feeds_dir.mkdir(exist_ok=True)
    output_file = feeds_dir / f"feed_{FEED_NAME}.xml"
    feed_generator.rss_file(str(output_file), pretty=True)
    logger.info(f"Saved RSS feed to {output_file}")
    return output_file


def main():
    cache = load_cache()
    html = fetch_page(BLOG_URL)
    new_articles = parse_articles(html)
    logger.info(f"Found {len(new_articles)} articles on page")
    posts = merge_articles(new_articles, cache["posts"])
    save_cache(posts)
    feed = generate_rss_feed(posts)
    save_rss_feed(feed)
    logger.info("Done!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate ABS-CBN Nation RSS feed")
    args = parser.parse_args()
    main()
