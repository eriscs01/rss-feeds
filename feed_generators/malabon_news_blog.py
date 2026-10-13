"""Malabon City Government News feed, read from the WordPress site's "news" category."""

import wordpress

BLOG_URL = "https://malabon.gov.ph/news/"
FEED_NAME = "malabon_news"
FEED_URL = "https://malabon.gov.ph/category/news/feed/"
SITE = wordpress.WordPressSite(
    author="Malabon City Government",
    logo_url="https://malabon.gov.ph/wp-content/uploads/2025/10/cropped-Ph_seal_Malabon2-192x192.png",
    # Post pages do not name their featured image, so the first post photo is the cover.
    cover_on_page=False,
)

if __name__ == "__main__":
    wordpress.run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Malabon City Government News",
        description="News and announcements from the Malabon City Government",
        feed_url=FEED_URL,
        site=SITE,
    )
