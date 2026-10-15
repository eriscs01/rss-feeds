##########################
### RSS Feed Generation ##
##########################

.PHONY: feeds_generate_all
feeds_generate_all: ## Generate all RSS feeds
	$(call check_venv)
	$(call print_info_section,Generating all RSS feeds)
	$(Q)uv run feed_generators/run_all_feeds.py
	$(call print_success,All feeds generated)

.PHONY: feeds_abscbn_nation
feeds_abscbn_nation: ## Generate RSS feed for ABS-CBN News Nation
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Nation feed)
	$(Q)uv run feed_generators/abscbn_nation_blog.py
	$(call print_success,ABS-CBN News Nation feed generated)

.PHONY: feeds_abscbn_regions
feeds_abscbn_regions: ## Generate RSS feed for ABS-CBN News Regions
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Regions feed)
	$(Q)uv run feed_generators/abscbn_regions_blog.py
	$(call print_success,ABS-CBN News Regions feed generated)

.PHONY: feeds_abscbn_world
feeds_abscbn_world: ## Generate RSS feed for ABS-CBN News World
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News World feed)
	$(Q)uv run feed_generators/abscbn_world_blog.py
	$(call print_success,ABS-CBN News World feed generated)

.PHONY: feeds_abscbn_health_science
feeds_abscbn_health_science: ## Generate RSS feed for ABS-CBN News Health & Science
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Health & Science feed)
	$(Q)uv run feed_generators/abscbn_health_science_blog.py
	$(call print_success,ABS-CBN News Health & Science feed generated)

.PHONY: feeds_abscbn_business
feeds_abscbn_business: ## Generate RSS feed for ABS-CBN News Business
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Business feed)
	$(Q)uv run feed_generators/abscbn_business_blog.py
	$(call print_success,ABS-CBN News Business feed generated)

.PHONY: feeds_abscbn_technology
feeds_abscbn_technology: ## Generate RSS feed for ABS-CBN News Technology
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Technology feed)
	$(Q)uv run feed_generators/abscbn_technology_blog.py
	$(call print_success,ABS-CBN News Technology feed generated)

.PHONY: feeds_abscbn_weather_traffic
feeds_abscbn_weather_traffic: ## Generate RSS feed for ABS-CBN News Weather & Traffic
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Weather & Traffic feed)
	$(Q)uv run feed_generators/abscbn_weather_traffic_blog.py
	$(call print_success,ABS-CBN News Weather & Traffic feed generated)

.PHONY: feeds_abscbn_calamity_hub
feeds_abscbn_calamity_hub: ## Generate RSS feed for ABS-CBN News Calamity Hub
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Calamity Hub feed)
	$(Q)uv run feed_generators/abscbn_calamity_hub_blog.py
	$(call print_success,ABS-CBN News Calamity Hub feed generated)

.PHONY: feeds_abscbn_factcheck
feeds_abscbn_factcheck: ## Generate RSS feed for ABS-CBN News Fact Check
	$(call check_venv)
	$(call print_info,Generating ABS-CBN News Fact Check feed)
	$(Q)uv run feed_generators/abscbn_factcheck_blog.py
	$(call print_success,ABS-CBN News Fact Check feed generated)

.PHONY: feeds_manilabulletin_philippines
feeds_manilabulletin_philippines: ## Generate RSS feed for Manila Bulletin Philippines
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin Philippines feed)
	$(Q)uv run feed_generators/manilabulletin_philippines_blog.py
	$(call print_success,Manila Bulletin Philippines feed generated)

.PHONY: feeds_manilabulletin_national
feeds_manilabulletin_national: ## Generate RSS feed for Manila Bulletin National
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin National feed)
	$(Q)uv run feed_generators/manilabulletin_national_blog.py
	$(call print_success,Manila Bulletin National feed generated)

.PHONY: feeds_manilabulletin_metro_manila
feeds_manilabulletin_metro_manila: ## Generate RSS feed for Manila Bulletin Metro Manila
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin Metro Manila feed)
	$(Q)uv run feed_generators/manilabulletin_metro_manila_blog.py
	$(call print_success,Manila Bulletin Metro Manila feed generated)

.PHONY: feeds_manilabulletin_luzon
feeds_manilabulletin_luzon: ## Generate RSS feed for Manila Bulletin Luzon
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin Luzon feed)
	$(Q)uv run feed_generators/manilabulletin_luzon_blog.py
	$(call print_success,Manila Bulletin Luzon feed generated)

.PHONY: feeds_manilabulletin_visayas
feeds_manilabulletin_visayas: ## Generate RSS feed for Manila Bulletin Visayas
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin Visayas feed)
	$(Q)uv run feed_generators/manilabulletin_visayas_blog.py
	$(call print_success,Manila Bulletin Visayas feed generated)

.PHONY: feeds_manilabulletin_mindanao
feeds_manilabulletin_mindanao: ## Generate RSS feed for Manila Bulletin Mindanao
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin Mindanao feed)
	$(Q)uv run feed_generators/manilabulletin_mindanao_blog.py
	$(call print_success,Manila Bulletin Mindanao feed generated)

.PHONY: feeds_manilabulletin_world
feeds_manilabulletin_world: ## Generate RSS feed for Manila Bulletin World
	$(call check_venv)
	$(call print_info,Generating Manila Bulletin World feed)
	$(Q)uv run feed_generators/manilabulletin_world_blog.py
	$(call print_success,Manila Bulletin World feed generated)

.PHONY: feeds_quezoncity_announcements
feeds_quezoncity_announcements: ## Generate RSS feed for Quezon City Government Announcements
	$(call check_venv)
	$(call print_info,Generating Quezon City Government Announcements feed)
	$(Q)uv run feed_generators/quezoncity_announcements_blog.py
	$(call print_success,Quezon City Government Announcements feed generated)

.PHONY: feeds_quezoncity_latest_news
feeds_quezoncity_latest_news: ## Generate RSS feed for Quezon City Government Latest News
	$(call check_venv)
	$(call print_info,Generating Quezon City Government Latest News feed)
	$(Q)uv run feed_generators/quezoncity_latest_news_blog.py
	$(call print_success,Quezon City Government Latest News feed generated)

.PHONY: feeds_quezoncity_featured_stories
feeds_quezoncity_featured_stories: ## Generate RSS feed for Quezon City Government Featured Stories
	$(call check_venv)
	$(call print_info,Generating Quezon City Government Featured Stories feed)
	$(Q)uv run feed_generators/quezoncity_featured_stories_blog.py
	$(call print_success,Quezon City Government Featured Stories feed generated)

.PHONY: clean_feeds
clean_feeds: ## Clean generated RSS feed files
	$(call print_warning,Removing generated RSS feeds)
	$(Q)rm -rf feeds/*.xml
	$(call print_success,RSS feeds removed)

.PHONY: feeds_makati_news
feeds_makati_news: ## Generate RSS feed for Makati City Government News
	$(call check_venv)
	$(call print_info,Generating Makati City Government News feed)
	$(Q)uv run feed_generators/makati_news_blog.py
	$(call print_success,Makati City Government News feed generated)

.PHONY: feeds_malabon_news
feeds_malabon_news: ## Generate RSS feed for Malabon City Government News
	$(call check_venv)
	$(call print_info,Generating Malabon City Government News feed)
	$(Q)uv run feed_generators/malabon_news_blog.py
	$(call print_success,Malabon City Government News feed generated)

.PHONY: feeds_mandaluyong_news
feeds_mandaluyong_news: ## Generate RSS feed for Mandaluyong City Government News
	$(call check_venv)
	$(call print_info,Generating Mandaluyong City Government News feed)
	$(Q)uv run feed_generators/mandaluyong_news_blog.py
	$(call print_success,Mandaluyong City Government News feed generated)

.PHONY: feeds_marikina_news
feeds_marikina_news: ## Generate RSS feed for Marikina City Government News
	$(call check_venv)
	$(call print_info,Generating Marikina City Government News feed)
	$(Q)uv run feed_generators/marikina_news_blog.py
	$(call print_success,Marikina City Government News feed generated)

.PHONY: feeds_pasay_city_events
feeds_pasay_city_events: ## Generate RSS feed for Pasay City Government City Events
	$(call check_venv)
	$(call print_info,Generating Pasay City Government City Events feed)
	$(Q)uv run feed_generators/pasay_city_events_blog.py
	$(call print_success,Pasay City Government City Events feed generated)

.PHONY: feeds_pasay_mayors_desk
feeds_pasay_mayors_desk: ## Generate RSS feed for Pasay City Government Mayor's Desk
	$(call check_venv)
	$(call print_info,Generating Pasay City Government Mayor's Desk feed)
	$(Q)uv run feed_generators/pasay_mayors_desk_blog.py
	$(call print_success,Pasay City Government Mayor's Desk feed generated)

.PHONY: feeds_pasay_pio_advisory
feeds_pasay_pio_advisory: ## Generate RSS feed for Pasay City Government PIO Advisory
	$(call check_venv)
	$(call print_info,Generating Pasay City Government PIO Advisory feed)
	$(Q)uv run feed_generators/pasay_pio_advisory_blog.py
	$(call print_success,Pasay City Government PIO Advisory feed generated)

.PHONY: feeds_pasig_news
feeds_pasig_news: ## Generate RSS feed for Pasig City Government News and Releases
	$(call check_venv)
	$(call print_info,Generating Pasig City Government News and Releases feed)
	$(Q)uv run feed_generators/pasig_news_blog.py
	$(call print_success,Pasig City Government News and Releases feed generated)

.PHONY: feeds_philippineairlines_press_releases
feeds_philippineairlines_press_releases: ## Generate RSS feed for Philippine Airlines Press Releases & Statements
	$(call check_venv)
	$(call print_info,Generating Philippine Airlines Press Releases & Statements feed)
	$(Q)uv run feed_generators/philippineairlines_press_releases_blog.py
	$(call print_success,Philippine Airlines Press Releases & Statements feed generated)

.PHONY: feeds_philippineairlines_travel_advisory
feeds_philippineairlines_travel_advisory: ## Generate RSS feed for Philippine Airlines Travel Advisory
	$(call check_venv)
	$(call print_info,Generating Philippine Airlines Travel Advisory feed)
	$(Q)uv run feed_generators/philippineairlines_travel_advisory_blog.py
	$(call print_success,Philippine Airlines Travel Advisory feed generated)

