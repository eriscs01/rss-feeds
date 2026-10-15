"""Philippine Airlines Travel Advisory feed, read from the "Travel Advisory" tab of the News & Events page."""

from philippineairlines import run

BLOG_URL = "https://www.philippineairlines.com/ph/en/newsevent-listingpage.html"
FEED_NAME = "philippineairlines_travel_advisory"
SECTION = "travel-advisory"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        section=SECTION,
        title="Philippine Airlines Travel Advisory",
        description="Travel advisories from Philippine Airlines",
    )
