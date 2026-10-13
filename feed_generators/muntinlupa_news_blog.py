"""Muntinlupa City Government News feed, read from the WordPress site's "news-announcement" category."""

import wordpress

BLOG_URL = "https://muntinlupacity.gov.ph/category/news-announcement/"
FEED_NAME = "muntinlupa_news"
FEED_URL = "https://muntinlupacity.gov.ph/category/news-announcement/feed/"
SITE = wordpress.WordPressSite(
    author="City Government of Muntinlupa",
    logo_url="https://muntinlupacity.gov.ph/wp-content/uploads/2022/10/Munti-logo.png",
    # Posts have no featured image, so the first post photo is the cover.
    cover_on_page=False,
)

if __name__ == "__main__":
    wordpress.run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Muntinlupa City Government News & Announcements",
        description="News and announcements from the City Government of Muntinlupa",
        feed_url=FEED_URL,
        site=SITE,
    )
