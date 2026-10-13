"""Quezon City Government Announcements feed, read from the site's "announcement" category."""

from quezoncity import run

BLOG_URL = "https://quezoncity.gov.ph/news-and-media/announcements/"
FEED_NAME = "quezoncity_announcements"
CATEGORY_SLUG = "announcement"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Quezon City Government Announcements",
        description="Announcements from the Quezon City Government",
        category_slug=CATEGORY_SLUG,
    )
