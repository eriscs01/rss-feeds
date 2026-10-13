"""Pasay City Government Mayor's Desk feed, read from the site's "mayors-desk" category."""

from pasay import run

BLOG_URL = "https://pasay.gov.ph/category/mayors-desk/"
FEED_NAME = "pasay_mayors_desk"
FEED_URL = "https://pasay.gov.ph/category/mayors-desk/feed/"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Pasay City Government Mayor's Desk",
        description="Mayor's Desk posts from the Pasay City Government",
        feed_url=FEED_URL,
    )
