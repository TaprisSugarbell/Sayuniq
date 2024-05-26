from source.config import BOT_NAME, LOGGING_LEVEL

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {"format": "[%(levelname)s || %(asctime)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{BOT_NAME}.log",
            "maxBytes": 3145728,
            "backupCount": 1,
            "formatter": "default",
        },
    },
    "loggers": {
        "": {"handlers": ["default", "file"], "level": "INFO", "propagate": False},
        "source.helper": {
            "handlers": ["default", "file"],
            "level": LOGGING_LEVEL,
            "propagate": False,
        },
    },
}
