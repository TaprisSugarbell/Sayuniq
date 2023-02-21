import asyncio
import logging
import os

import pyrogram

from source.helpers.logger_config import log_file
from source.helpers.mongo_connect import Mongo, confirm
from source.config import (
    LOG_CHANNEL,
    BOT_NAME,
    BOT_TOKEN,
    API_ID,
    API_HASH,
    human_hour_readable,
)
from source.helpers.utils import create_folder
from source.locales import get_string


logger = logging.getLogger(__name__)
sayu_logger = logging.getLogger(BOT_NAME)
PACKAGE = __package__


# Client
plugins = dict(root=f"source/plugins")

app = pyrogram.Client(
    name=BOT_NAME,
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=plugins,
    in_memory=True,
)


async def auth_users():
    users = Mongo(database=BOT_NAME, collection="users")
    confirmed = await confirm(users, {})
    return [i["user_id"] for i in confirmed] if confirmed else []


async def logs_channel_update(
    message: str = None,
    mode: str = "send_message",
    client: pyrogram.Client = None,
    *args,
    **kwargs,
):
    if message is None:
        message = get_string("log_channel").format(
            bot_name=BOT_NAME, date=human_hour_readable()
        )

    client = client or app
    send_mode = ["send_message", "edit_message_text"]
    text = {"text": message} if mode in send_mode else {mode.split("_")[-1]: message}

    kwargs |= text
    await getattr(client, mode)(chat_id=LOG_CHANNEL, *args, **kwargs)
    if os.path.exists(message) and message != log_file:
        os.remove(message)


queue_ = asyncio.PriorityQueue()
