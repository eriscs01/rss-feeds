"""Presidential Communications Office News Releases feed.

The listing page (https://pco.gov.ph/news-releases/) shows the posts of the
WordPress site's "news_releases" post type, which has its own native RSS feed.
"""

import wordpress

BLOG_URL = "https://pco.gov.ph/news-releases/"
FEED_NAME = "pco_news_releases"
FEED_URL = "https://pco.gov.ph/news_releases/feed/"
SITE = wordpress.WordPressSite(
    author="Presidential Communications Office",
    logo_url="https://pco.gov.ph/wp-content/uploads/2024/09/cropped-pco_icon_144px-1-192x192.png",
    # The feed carries only an excerpt, so the post photo is read from the page.
    body_selector="article .entry-content img",
    # Every post page reports this logo as its share image, whatever its own photo is.
    placeholder_covers=(
        "https://mirror.pco.gov.ph/wp-content/uploads/2025/09/pco_logo_news_releases_featured_photo_.png",
    ),
    excerpt_more="Read More",
)

if __name__ == "__main__":
    wordpress.run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Presidential Communications Office News Releases",
        description="News releases from the Presidential Communications Office of the Philippines",
        feed_url=FEED_URL,
        site=SITE,
    )
