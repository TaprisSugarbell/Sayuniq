from Sayuniq.helper.utils import create_folder
from Sayuniq.__vars__ import BOT_NAME, LOGGING_LEVEL

__dr, __file = "./logs/", f"{BOT_NAME}.log"
log_file = __dr + __file
create_folder(temp_folder=__dr), create_folder(temp_folder="./sayureports/")
# DEBUG
_dbt = "-----------------------------------------------------------" \
       "------------------------------------------------------------"

LOGGER_CONFIG = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(levelname)s || %(asctime)s] %(name)s: %(message)s"
            },
            BOT_NAME: {
                "format": f"{_dbt}\n[%(levelname)s || %(hhr)s] REASON = \"%(message)s\"\n"
            }
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "default",
                "class": "logging.StreamHandler"
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
            BOT_NAME: {
                "handlers": [
                    "default", "file"
                ],
                "level": LOGGING_LEVEL,
                "propagate": False
            },
            # "__main__": {
            #     "handlers": [
            #         "default"
            #     ],
            #     "level": "DEBUG",
            #     "propagate": False
            # }
        }
    }


