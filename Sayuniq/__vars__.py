from decouple import config
from datetime import datetime
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
CHID = config("CHANNEL_ID", default=None)
LOG_CHANNEL = config("LOG_CHANNEL", default=None, cast=int)
TESTS_CHANNEL = config("TESTS_CHANNEL", default=None, cast=int)

# DATETIME
HOUR_FORMAT = 1 if config("HOUR_FORMAT", default=0, cast=int) == 24 else 0
HUMAN_HOUR_READABLE = datetime.now().strftime(
    f"{get_string('format_date').format(datetime.now().month)} "
    f"{get_string('format_hour')[HOUR_FORMAT]}"
)
# LOGGER
LOGGING_LEVEL = config("LOGGING_LEVEL", default="WARNING")

try:
    CHANNEL_ID = int(CHID)
except ValueError:
    CHANNEL_ID = CHID
