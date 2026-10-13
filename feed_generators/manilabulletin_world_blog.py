"""Manila Bulletin World feed, read from the category page's "Latest" listing."""

from manilabulletin import run

BLOG_URL = "https://mb.com.ph/category/world"
FEED_NAME = "manilabulletin_world"
SECTION_ID = 26
SUBSECTION_ID = None

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Manila Bulletin World",
        description="Latest World news from Manila Bulletin",
        section_id=SECTION_ID,
        subsection_id=SUBSECTION_ID,
    )
