import os
import logging
import cloudscraper
from logging.config import dictConfig
from Sayuniq.helper.logger_configs.logger_config import LOGGER_CONFIG

PARSER = "html.parser"
requests = cloudscraper.create_scraper(cloudscraper.Session)

dictConfig(LOGGER_CONFIG)

logger = logging.getLogger(__name__)


async def configure_wd():
    if "main.py" in os.listdir():
       os.chdir("../")
    logger.debug("Work Directory configured!")
