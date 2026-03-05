##########################
### RSS Feed Generation ##
##########################

.PHONY: feeds_generate_all
feeds_generate_all: ## Generate all RSS feeds
	$(call check_venv)
	$(call print_info_section,Generating all RSS feeds)
	$(Q)python feed_generators/run_all_feeds.py
	$(call print_success,All feeds generated)

.PHONY: feeds_pna_national
feeds_pna_national: ## Generate RSS feed for PNA National (incremental)
	$(call check_venv)
	$(call print_info,Generating PNA National feed)
	$(Q)python feed_generators/pna_national_blog.py
	$(call print_success,PNA National feed generated)

.PHONY: feeds_pna_national_full
feeds_pna_national_full: ## Generate RSS feed for PNA National (full reset)
	$(call check_venv)
	$(call print_info,Generating PNA National feed - FULL RESET)
	$(Q)python feed_generators/pna_national_blog.py --full
	$(call print_success,PNA National feed generated - full reset)

.PHONY: clean_feeds
clean_feeds: ## Clean generated RSS feed files
	$(call print_warning,Removing generated RSS feeds)
	$(Q)rm -rf feeds/*.xml
	$(call print_success,RSS feeds removed)
