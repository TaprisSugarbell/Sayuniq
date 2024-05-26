import logging

import hydrogram

from source.config import (API_HASH, API_ID, BOT_NAME, BOT_TOKEN, LOG_CHANNEL,
                           human_hour_readable)
from source.helpers.mongo_connect import Mongo, confirm
from source.locales import get_string

logger = logging.getLogger(__name__)
sayu_logger = logging.getLogger(BOT_NAME)

# Client
plugins = dict(root="source/plugins")

app = hydrogram.Client(
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
