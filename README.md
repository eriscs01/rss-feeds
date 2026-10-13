# RSS Feeds

Fork of [Olshansk/rss-feeds](https://github.com/Olshansk/rss-feeds).

## Available Feeds

| Blog | Feed |
| ---- | ---- |
| [ABS-CBN News Business](https://www.abs-cbn.com/news/business) | [feed_abscbn_business.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_business.xml) |
| [ABS-CBN News Calamity Hub](https://www.abs-cbn.com/calamity-hub) | [feed_abscbn_calamity_hub.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_calamity_hub.xml) |
| [ABS-CBN News Fact Check](https://www.abs-cbn.com/news/factcheck) | [feed_abscbn_factcheck.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_factcheck.xml) |
| [ABS-CBN News Health & Science](https://www.abs-cbn.com/news/health-science) | [feed_abscbn_health_science.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_health_science.xml) |
| [ABS-CBN News Nation](https://www.abs-cbn.com/news/nation) | [feed_abscbn_nation.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_nation.xml) |
| [ABS-CBN News Regions](https://www.abs-cbn.com/news/regions) | [feed_abscbn_regions.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_regions.xml) |
| [ABS-CBN News Technology](https://www.abs-cbn.com/news/technology) | [feed_abscbn_technology.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_technology.xml) |
| [ABS-CBN News Weather & Traffic](https://www.abs-cbn.com/news/weather-traffic) | [feed_abscbn_weather_traffic.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_weather_traffic.xml) |
| [ABS-CBN News World](https://www.abs-cbn.com/news/world) | [feed_abscbn_world.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_abscbn_world.xml) |
| [Manila Bulletin Luzon](https://mb.com.ph/category/luzon) | [feed_manilabulletin_luzon.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_luzon.xml) |
| [Manila Bulletin Metro Manila](https://mb.com.ph/category/metro-manila) | [feed_manilabulletin_metro_manila.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_metro_manila.xml) |
| [Manila Bulletin Mindanao](https://mb.com.ph/category/mindanao) | [feed_manilabulletin_mindanao.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_mindanao.xml) |
| [Manila Bulletin National](https://mb.com.ph/category/national) | [feed_manilabulletin_national.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_national.xml) |
| [Manila Bulletin Philippines](https://mb.com.ph/category/philippines) | [feed_manilabulletin_philippines.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_philippines.xml) |
| [Manila Bulletin Visayas](https://mb.com.ph/category/visayas) | [feed_manilabulletin_visayas.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_visayas.xml) |
| [Manila Bulletin World](https://mb.com.ph/category/world) | [feed_manilabulletin_world.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_manilabulletin_world.xml) |
| [Quezon City Government Announcements](https://quezoncity.gov.ph/news-and-media/announcements/) | [feed_quezoncity_announcements.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_quezoncity_announcements.xml) |
| [Quezon City Government Featured Stories](https://quezoncity.gov.ph/news-and-media/featured-stories/) | [feed_quezoncity_featured_stories.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_quezoncity_featured_stories.xml) |
| [Quezon City Government Latest News](https://quezoncity.gov.ph/news-and-media/latest-news/) | [feed_quezoncity_latest_news.xml](https://raw.githubusercontent.com/eriscs01/rss-feeds/main/feeds/feed_quezoncity_latest_news.xml) |

## Official Feeds

Other Philippine news outlets publish their own RSS feeds, so no generator is needed for these.

| Outlet | Feed |
| ------ | ---- |
| GMA News | <https://data.gmanews.tv/gno/rss/news/feed.xml> |
| Inquirer Business | <http://business.inquirer.net/feed> |
| Inquirer Cebu Daily News | <http://cebudailynews.inquirer.net/feed> |
| Inquirer Entertainment | <http://entertainment.inquirer.net/feed> |
| Inquirer Global Nation | <http://globalnation.inquirer.net/feed> |
| Inquirer Lifestyle | <http://lifestyle.inquirer.net/feed> |
| Inquirer Nation | <http://newsinfo.inquirer.net/category/inquirer-headlines/nation/feed> |
| Inquirer News | <http://newsinfo.inquirer.net/feed> |
| Inquirer Opinion | <http://opinion.inquirer.net/feed> |
| Inquirer Sports | <http://sports.inquirer.net/feed> |
| Inquirer Technology | <http://technology.inquirer.net/feed> |
| Manila Times News | <https://www.manilatimes.net/news/feed/> |
| Philstar Business | <http://www.philstar.com/rss/business> |
| Philstar Entertainment | <http://www.philstar.com/rss/entertainment> |
| Philstar Headlines | <http://www.philstar.com/rss/headlines> |
| Philstar Nation | <http://www.philstar.com/rss/nation> |
| Philstar Opinion | <http://www.philstar.com/rss/opinion> |
| Philstar Sports | <http://www.philstar.com/rss/sports> |
| Philstar World | <http://www.philstar.com/rss/world> |
| Rappler | <https://www.rappler.com/feed/> |

## Development

Feeds are registered in [feeds.yaml](feeds.yaml) and regenerated hourly by [run_feeds.yml](.github/workflows/run_feeds.yml).
See [AGENTS.md](AGENTS.md) and [feed reliability and shared patterns](docs/feed-reliability.md).
