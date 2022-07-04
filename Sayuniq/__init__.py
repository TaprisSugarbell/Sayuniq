import asyncio
import logging
import os
from logging import handlers

import pyrogram

from Sayuniq.helper.mongo_connect import Mongo, confirm
from __vars__ import *
from helper.utils import create_folder
from strings import get_string

__dr, __file = "./logs/", f"{BOT_NAME}.log"
log_file = __dr + __file
create_folder(temp_folder=__dr), create_folder(temp_folder="./sayureports/")

# DEBUG
_dbt = "-----------------------------------------------------------" \
       "------------------------------------------------------------"
logging.basicConfig(format=f'{_dbt}\n[%(levelname)s || %(hhr)s] '
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
        sayulog.info(msg, extra={"hhr": human_hour_readable()})
        sayulog.setLevel(LOGGING_LEVEL)
    else:
        sayulog.info(msg, extra={"hhr": human_hour_readable()})


# Client
plugins = dict(root=f"{BOT_NAME}/plugins")
app = pyrogram.Client(BOT_NAME, bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, plugins=plugins)


async def auth_users():
    _u = Mongo(database=BOT_NAME, collection="users")
    _c = await confirm(_u, {})
    if _c:
        return [i["user_id"] for i in _c]
    else:
        return []


async def logs_channel_update(
        message: str = None,
        _mode: str = "send_message",
        _app=None,
        *args,
        **kwargs
):
    if message is None:
        message = get_string(
            "log_channel"
        ).format(
            bot_name=BOT_NAME,
            date=human_hour_readable()
        )
    _snd_Txt = ["send_message", "edit_message_text"]
    t__ = {"text": message} if _mode in _snd_Txt else {_mode.split("_")[-1]: message}
    kwargs.update(t__)
    if _app:
        await getattr(_app, _mode)(LOG_CHANNEL, *args, **kwargs)
    else:
        await getattr(app, _mode)(LOG_CHANNEL, *args, **kwargs)
    if os.path.exists(message) and message != log_file:
        os.remove(message)


queue_ = asyncio.PriorityQueue()

