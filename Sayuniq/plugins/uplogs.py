import os
from ..strings import get_string
from pyrogram import Client, filters
from .. import logs_channel_update, log_file, auth_users, BOT_NAME


@Client.on_message(filters.command(["log", "logs"]))
async def __ulgs__(bot, update):
    print(update)
    user_id = update.from_user.id
    AUTH_USERS = await auth_users()
    if user_id == 784148805 or user_id in AUTH_USERS:
        if os.path.getsize(log_file) > 0:
            await logs_channel_update(log_file, "send_document",
                                      caption=get_string("document_log").format(BOT_NAME),
                                      _app=bot
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
            await logs_channel_update(log_file, "send_document",
                                      caption=get_string("document_log").format(BOT_NAME),
                                      _app=bot
                                      )
    else:
        print(user_id)



