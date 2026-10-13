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

.PHONY: clean_feeds
clean_feeds: ## Clean generated RSS feed files
	$(call print_warning,Removing generated RSS feeds)
	$(Q)rm -rf feeds/*.xml
	$(call print_success,RSS feeds removed)
