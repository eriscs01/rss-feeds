"""Pasay City Government City Events feed, read from the site's "events" post type."""

from pasay import run

BLOG_URL = "https://pasay.gov.ph/balita/city-events/"
FEED_NAME = "pasay_city_events"
FEED_URL = "https://pasay.gov.ph/events/feed/"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Pasay City Government City Events",
        description="City events from the Pasay City Government",
        feed_url=FEED_URL,
    )
