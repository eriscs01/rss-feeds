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

.PHONY: clean_feeds
clean_feeds: ## Clean generated RSS feed files
	$(call print_warning,Removing generated RSS feeds)
	$(Q)rm -rf feeds/*.xml
	$(call print_success,RSS feeds removed)
