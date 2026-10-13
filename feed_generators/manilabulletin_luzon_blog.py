"""Manila Bulletin Luzon feed, read from the category page's "Latest" listing."""

from manilabulletin import run

BLOG_URL = "https://mb.com.ph/category/luzon"
FEED_NAME = "manilabulletin_luzon"
SECTION_ID = 25
SUBSECTION_ID = 84

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Manila Bulletin Luzon",
        description="Latest Luzon news from Manila Bulletin",
        section_id=SECTION_ID,
        subsection_id=SUBSECTION_ID,
    )
