"""Manila Bulletin Philippines feed, read from the category page's "Latest" listing."""

from manilabulletin import run

BLOG_URL = "https://mb.com.ph/category/philippines"
FEED_NAME = "manilabulletin_philippines"
SECTION_ID = 25
SUBSECTION_ID = None

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Manila Bulletin Philippines",
        description="Latest Philippines news from Manila Bulletin",
        section_id=SECTION_ID,
        subsection_id=SUBSECTION_ID,
    )
