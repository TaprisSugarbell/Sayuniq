import os
import logging
from ..locales import get_string
from pyrogram import Client, filters, types
from ..config import LOG_CHANNEL, human_hour_readable
from .. import log_file, auth_users


@Client.on_message(filters.command(["log", "logs"]))
async def __ulgs__(bot: Client, update: types.Message):
    user_id = update.from_user.id
    AUTH_USERS = await auth_users()
    if user_id == 784148805 or user_id in AUTH_USERS:
        if os.path.getsize(log_file) > 0:
            await bot.send_document(
                LOG_CHANNEL,
                log_file,
                caption=get_string("document_log").format(
                    bot_name=bot.me.first_name, date=human_hour_readable()
                ),
            )
            await bot.send_message(user_id, "Listo.")
        else:
            await bot.send_message(user_id, f"No hay log.\n\"{os.listdir('./logs/')}\"")
            await bot.send_document(
                LOG_CHANNEL,
                log_file,
                caption=get_string("document_log").format(
                    bot_name=bot.me.first_name, date=human_hour_readable()
                ),
            )
    else:
        logging.info("Quiso ver los logs: %s", user_id)
