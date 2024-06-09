# ------------------- Scrapy settings -------------------
# Note: These settings are overwritten by the settings in the main.py file when the crawler is run
#       -> might not be up-to-date

# The name of the scrapy project
BOT_NAME = 'facr_scraper'

# The path to the spider modules
SPIDER_MODULES = ['facr_scraper.spiders']
NEWSPIDER_MODULE = 'facr_scraper.spiders'

# The pipelines used to process the scraped data
ITEM_PIPELINES = {
        'facr_scraper.pipelines.FacrscraperPipeline': 300,
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Suppress the logging messages
LOG_ENABLED = False