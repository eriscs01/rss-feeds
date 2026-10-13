"""Shared generator for the Quezon City Government news feeds.

Each News and Media listing page (https://quezoncity.gov.ph/news-and-media/<name>/)
shows the posts of one WordPress category. The site publishes a native RSS feed
per category that lists the same posts with exact publish times, but without
any images. Each ``quezoncity_*_blog.py`` script reads its category feed, then
fetches each new post's page for its cover photo and inline images and turns
them into an HTML block for ``content:encoded``.
"""

import wordpress

CATEGORY_FEED_URL = "https://quezoncity.gov.ph/category/{}/feed/"
SITE = wordpress.WordPressSite(
    author="Quezon City Government",
    logo_url="https://quezoncity.gov.ph/wp-content/themes/qcproject/images/favicon.png",
    # The category feed carries only an excerpt, so post photos are read from the page.
    body_selector="article .single-post-inner img",
    first_image_as_cover=False,
    # Kept as published: cleaning would rewrite the summaries of items already in the feeds.
    clean_excerpts=False,
)


def run(feed_name, blog_url, title, description, category_slug):
    """Refresh one category feed: fetch, merge with the cache, write the XML."""
    return wordpress.run(feed_name, blog_url, title, description, CATEGORY_FEED_URL.format(category_slug), SITE)
