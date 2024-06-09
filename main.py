import yaml

from scrapy.crawler import CrawlerProcess

from src.facr_scraper.facr_scraper.spiders.match_spider import MatchSpider


def main():
    # ----------- Extract the project configuration -----------
    # Load the configuration file
    config = yaml.safe_load(open("cfg/config.yaml"))

    # Extract the information from the configuration file
    obey_robots_txt = config["scraper"]["obey_robots_txt"]
    target_team = config["scraper"]["target_team"]
    base_url = config["scraper"]["base_url"]
    central_url = config["scraper"]["central_url"]
    cookie_php_session = config["scraper"]["cookie_php_session"]
    scrape_data = config["project"]["scrape_data"]

    if scrape_data:
        # ----------- Scrape the data from the website and store it in the database -----------
        print("- Scraping the data from the website and storing it in the database...")
        # Prepare the settings for the crawler
        settings = {
            "BOT_NAME": "fact_scraper",
            "SPIDER_MODULES": ["src.facr_scraper.facr_scraper.spiders"],
            "NEWSPIDER_MODULE": "src.facr_scraper.facr_scraper.spiders",
            "ROBOTSTXT_OBEY": obey_robots_txt,
            "ITEM_PIPELINES": {
                "src.facr_scraper.facr_scraper.pipelines.FacrscraperPipeline": 300},
            "LOG_ENABLED": False
        }

        # Create a crawler process
        process = CrawlerProcess(settings)

        # Add the spider with the configured arguments to the process
        print(" -> Start scraping...")
        process.crawl(MatchSpider, target_team=target_team, base_url=base_url, central_url=central_url,
                      cookie=cookie_php_session)

        # Start the crawling process
        process.start()
    else:
        print("- Skipping the scraping process...")


if __name__ == "__main__":
    main()
