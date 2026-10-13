"""Shared generator for the Pasay City Government news feeds.

The site runs on WordPress. Each "Balita" listing page shows the posts of one
category, or the "events" post type, and the site publishes a native RSS feed
for each. Each ``pasay_*_blog.py`` script reads its native feed for the posts
and their inline photos, then fetches each new post's page for its cover photo.
"""

import wordpress

SITE = wordpress.WordPressSite(
    author="Pasay City Government",
    # The site's only icon is an SVG, which feed readers do not show, so the seal
    # inside it is kept in this repository as a PNG.
    logo_url="https://raw.githubusercontent.com/eriscs01/rss-feeds/main/assets/icons/pasay.png",
    placeholder_covers=("https://pasay.gov.ph/wp-content/uploads/2026/08/pasay-city-social.png",),
)


def run(feed_name, blog_url, title, description, feed_url):
    """Refresh one feed from the native RSS feed at ``feed_url``."""
    return wordpress.run(feed_name, blog_url, title, description, feed_url, SITE)
