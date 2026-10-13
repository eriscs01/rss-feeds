"""Manila Bulletin National feed, read from the category page's "Latest" listing."""

from manilabulletin import run

BLOG_URL = "https://mb.com.ph/category/national"
FEED_NAME = "manilabulletin_national"
SECTION_ID = 25
SUBSECTION_ID = 82

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Manila Bulletin National",
        description="Latest National news from Manila Bulletin",
        section_id=SECTION_ID,
        subsection_id=SUBSECTION_ID,
    )
