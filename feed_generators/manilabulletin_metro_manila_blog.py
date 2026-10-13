"""Manila Bulletin Metro Manila feed, read from the category page's "Latest" listing."""

from manilabulletin import run

BLOG_URL = "https://mb.com.ph/category/metro-manila"
FEED_NAME = "manilabulletin_metro_manila"
SECTION_ID = 25
SUBSECTION_ID = 83

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Manila Bulletin Metro Manila",
        description="Latest Metro Manila news from Manila Bulletin",
        section_id=SECTION_ID,
        subsection_id=SUBSECTION_ID,
    )
