"""Pasay City Government PIO Advisory feed, read from the site's "pio-advisory" category."""

from pasay import run

BLOG_URL = "https://pasay.gov.ph/category/pio-advisory/"
FEED_NAME = "pasay_pio_advisory"
FEED_URL = "https://pasay.gov.ph/category/pio-advisory/feed/"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Pasay City Government PIO Advisory",
        description="Public Information Office advisories from the Pasay City Government",
        feed_url=FEED_URL,
    )
