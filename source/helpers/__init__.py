import logging
from logging.config import dictConfig

import cloudscraper

from source.helpers.logger_config import LOGGER_CONFIG

PARSER = "html.parser"
requests = cloudscraper.create_scraper(cloudscraper.Session)

dictConfig(LOGGER_CONFIG)

logger = logging.getLogger(__name__)
