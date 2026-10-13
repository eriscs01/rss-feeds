"""Quezon City Government Latest News feed, read from the site's "latest-news" category."""

from quezoncity import run

BLOG_URL = "https://quezoncity.gov.ph/news-and-media/latest-news/"
FEED_NAME = "quezoncity_latest_news"
CATEGORY_SLUG = "latest-news"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Quezon City Government Latest News",
        description="Latest news and press releases from the Quezon City Government",
        category_slug=CATEGORY_SLUG,
    )
