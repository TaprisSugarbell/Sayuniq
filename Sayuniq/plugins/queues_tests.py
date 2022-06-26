import random
from .. import queue_
from ..helper.utils import rankey
from ..helper.mongo_connect import *
from pyrogram import Client, filters


@Client.on_message(filters.command(["q"]))
async def __queue__(bot, update):
    print(update)
    queue_.put(
        (
            random.randint(0, 9),
            {
                "user_id": update.from_user.id,
                "chat_id": update.chat.id,
                "text": update.text
            }
        )
    )


@Client.on_callback_query(filters.regex("mty_.*"))
async def __mty__(bot, update):
    print(update)


