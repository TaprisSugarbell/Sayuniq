import os
from ..strings import get_string
from pyrogram import Client, filters
from ..__vars__ import LOG_CHANNEL, BOT_NAME, human_hour_readable
from .. import log_file, auth_users


@Client.on_message(filters.command(["log", "logs"]))
async def __ulgs__(bot, update):
    print(update)
    user_id = update.from_user.id
    AUTH_USERS = await auth_users()
    if user_id == 784148805 or user_id in AUTH_USERS:
        if os.path.getsize(log_file) > 0:
            await bot.send_document(
                LOG_CHANNEL,
                log_file,
                caption=get_string("document_log").format(
                    bot_name=BOT_NAME,
                    date=human_hour_readable()
                )
            )
            await bot.send_message(
                user_id,
                "Listo."
            )
        else:
            await bot.send_message(
                user_id,
                f"No hay log.\n\"{os.listdir('./logs/')}\""
            )
            await bot.send_document(
                LOG_CHANNEL,
                log_file,
                caption=get_string("document_log").format(
                    bot_name=BOT_NAME,
                    date=human_hour_readable()
                )
            )
    else:
        print(user_id)



