import logging
import os

from hydrogram import Client, filters, types

from source import auth_users
from source.config import LOG_CHANNEL, human_hour_readable, BOT_NAME
from source.locales import get_string


@Client.on_message(filters.command(["log", "logs"]))
async def __ulgs__(bot: Client, message: types.Message):
    user_id = message.from_user.id
    AUTH_USERS = await auth_users()
    if user_id == 784148805 or user_id in AUTH_USERS:
        if os.path.getsize(f"{BOT_NAME}.log") > 0:
            await bot.send_document(
                chat_id=LOG_CHANNEL,
                document=f"{BOT_NAME}.log",
                caption=get_string("document_log").format(
                    bot_name=bot.me.first_name, date=human_hour_readable()
                ),
            )
            await bot.send_message(chat_id=user_id, text="Listo.")
        else:
            await bot.send_message(
                chat_id=user_id, text=f"No hay log.\n\"{os.listdir('./logs/')}\""
            )
            await bot.send_document(
                chat_id=LOG_CHANNEL,
                document=log_file,
                caption=get_string("document_log").format(
                    bot_name=bot.me.first_name, date=human_hour_readable()
                ),
            )
    else:
        logging.info("Quiso ver los logs: %s", user_id)
