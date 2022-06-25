import os
import logging
import pyrogram
from __vars__ import *
from logging import handlers
from strings import get_string
from queue import PriorityQueue
from helper.utils import create_folder

__dr, __file = "./logs/", f"{BOT_NAME}.log"
log_file = __dr + __file
create_folder(temp_folder=__dr), create_folder(temp_folder="./sayureports/")

# DEBUG
_dbt = "-----------------------------------------------------------" \
       "------------------------------------------------------------"
logging.basicConfig(format=f'{_dbt}\n[%(levelname)s || {HUMAN_HOUR_READABLE}] '
                           f'REASON = "%(message)s"\n',
                    level=getattr(logging, LOGGING_LEVEL),
                    handlers=[
                        handlers.RotatingFileHandler(
                            filename=log_file,
                            maxBytes=3145728,
                            backupCount=1
                        ),
                        logging.StreamHandler()
                    ]
                    )
sayulog = logging.getLogger(BOT_NAME)


def logging_stream_info(msg):
    if LOGGING_LEVEL != "INFO":
        sayulog.setLevel("INFO")
        sayulog.info(msg)
        sayulog.setLevel(LOGGING_LEVEL)
    else:
        sayulog.info(msg)


# Client
plugins = dict(root=f"{BOT_NAME}/plugins")
app = pyrogram.Client(BOT_NAME, bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, plugins=plugins)


async def logs_channel_update(
        message: str =
        get_string(
            "log_channel"
        ).format(
            BOT_NAME,
            HUMAN_HOUR_READABLE
        ),
        _mode: str = "send_message",
        *args,
        **kwargs
):
    await getattr(app, _mode)(LOG_CHANNEL, message, *args, **kwargs)
    if os.path.exists(message):
        os.remove(message)


queue_ = PriorityQueue()

