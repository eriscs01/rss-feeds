"""Philippine Airlines Press Releases & Statements feed, read from the "Press releases statements" tab of the News & Events page."""

from philippineairlines import run

BLOG_URL = "https://www.philippineairlines.com/ph/en/newsevent-listingpage.html"
FEED_NAME = "philippineairlines_press_releases"
SECTION = "press-releases-statements"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        section=SECTION,
        title="Philippine Airlines Press Releases & Statements",
        description="Press releases and statements from Philippine Airlines",
    )
