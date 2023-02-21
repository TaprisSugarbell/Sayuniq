from source.helpers.utils import create_folder
from source.config import BOT_NAME, LOGGING_LEVEL

__dr, __file = "./logs/", f"{BOT_NAME}.log"
log_file = __dr + __file
create_folder(temp_folder=__dr), create_folder(temp_folder="./sayureports/")

LOGGER_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(levelname)s || %(asctime)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            },
            "file": {
                  "class": "logging.handlers.RotatingFileHandler",
                  "filename": log_file,
                  "maxBytes": 3145728,
                  "backupCount": 1,
                  "formatter": "default"
                }
        },
        "loggers": {
            "": {
                "handlers": [
                    "default", "file"
                ],
                "level": "INFO",
                "propagate": False
            },
            "SayuWaifu.helper": {
                "handlers": [
                    "default", "file"
                ],
                "level": LOGGING_LEVEL,
                "propagate": False
            }
        }
    }


