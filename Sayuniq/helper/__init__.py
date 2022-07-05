import cloudscraper
from logging.config import dictConfig
from Sayuniq.helper.logger_configs.logger_config import LOGGER_CONFIG

PARSER = "html.parser"
requests = cloudscraper.create_scraper(cloudscraper.Session)

dictConfig(LOGGER_CONFIG)
