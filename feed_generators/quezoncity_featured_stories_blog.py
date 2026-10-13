"""Quezon City Government Featured Stories feed, read from the site's "featured-stories" category."""

from quezoncity import run

BLOG_URL = "https://quezoncity.gov.ph/news-and-media/featured-stories/"
FEED_NAME = "quezoncity_featured_stories"
CATEGORY_SLUG = "featured-stories"

if __name__ == "__main__":
    run(
        feed_name=FEED_NAME,
        blog_url=BLOG_URL,
        title="Quezon City Government Featured Stories",
        description="Featured stories from the Quezon City Government",
        category_slug=CATEGORY_SLUG,
    )
