from datetime import datetime, timedelta, timezone

from decouple import config

from strings import get_string

# Version
__version__tuple__ = ("0", "0", "1")

__version__ = ".".join(__version__tuple__)
__version_short__ = ".".join(__version__tuple__[:-1])

#   # CONSTANTS
# Database 8 Restrictions
MONGO_URL = config("MONGO_URL", default=None)
AUTH_USERS = config("AUTH_USERS", default=None)
# Data
BOT_NAME = config("BOT_NAME", default="Sayuniq")
API_ID = config("API_ID", default=None, cast=int)
API_HASH = config("API_HASH", default=None)
BOT_TOKEN = config("BOT_TOKEN", default=None)
BOT_ALIAS = config("BOT_ALIAS", default="Sayuniq")
# Channels id
UTC = config("UTC", default="-6")
CHANNEL_ID = config("CHANNEL_ID", default=None)
LOG_CHANNEL = config("LOG_CHANNEL", default=None, cast=int)
TESTS_CHANNEL = config("TESTS_CHANNEL", default=None, cast=int)

# DATETIME
HOUR_FORMAT = 1 if config("HOUR_FORMAT", default=0, cast=int) == 24 else 0

# LOGGER
LOGGING_LEVEL = config("LOGGING_LEVEL", default="WARNING")

# SCRAPPER
USER_AGENT = {"user-agent": config("USER_AGENT", default=f"{BOT_ALIAS}/{__version__}")}


def human_hour_readable(hformat=HOUR_FORMAT, _utc=UTC):
    if ":" in UTC:
        _hours, _minutes = UTC.split(":")
    else:
        _hours, _minutes = UTC, 0
    return datetime.now(timezone(timedelta(hours=int(_hours), minutes=int(_minutes)))).strftime(
        f"{get_string('format_date').format(datetime.now().month)} "
        f"{get_string('format_hour')[hformat]}")
