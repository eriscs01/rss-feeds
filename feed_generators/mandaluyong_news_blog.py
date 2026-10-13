"""Mandaluyong City Government News feed, read from the WordPress site's "news" category."""

import wordpress

BLOG_URL = "https://mandaluyong.gov.ph/news/"
FEED_NAME = "mandaluyong_news"
FEED_URL = "https://mandaluyong.gov.ph/category/news/feed/"
SITE = wordpress.WordPressSite(
    author="Mandaluyong City Government",
    logo_url="https://mandaluyong.gov.ph/storage/2020/03/Ph_seal_Mandaluyong.png",
    # The site serves its uploads under /storage/ as well.
    upload_paths=("/wp-content/uploads/", "/storage/"),
)

if __name__ == "__main__":
    wordpress.run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Mandaluyong City Government News",
        description="News from the Mandaluyong City Government",
        feed_url=FEED_URL,
        site=SITE,
    )
