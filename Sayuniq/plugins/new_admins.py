from pyrogram import Client, filters

from .. import auth_users, BOT_NAME
from ..helper.mongo_connect import *

_u = Mongo(URI, BOT_NAME, "users")


@Client.on_message(filters.command(["add", "watch", "delete", "del"]))
async def __add_and_delete_admins__(bot, update):
    print(update)
    data = ""
    chat_id = update.chat.id
    mm = update.text.split()
    mode = mm[0].replace("/", "")
    if update.from_user.id == 784148805:
        AUTH_USERS = await auth_users()
        if len(mm) == 1:
            pass
        else:
            data = update.text.split()[1].strip()
        if len(data) == 0 and mode != "watch":
            await bot.send_message(chat_id,
                                   "Debes ingresar un id de un usuario.")
        else:
            if mode == "add":
                try:
                    user_id = int(data)
                    _ui = {"user_id": user_id}
                    _c = await confirm(_u, _ui)
                    if _c:
                        await bot.send_message(chat_id,
                                               f'"{user_id}" ya se encuentra en la base de datos.')
                    else:
                        await add_(_u, _ui)
                        await bot.send_message(chat_id,
                                               f'Se agrego "{user_id}" a la base de datos.')
                except ValueError:
                    await bot.send_message(chat_id,
                                           "El valor debe de ser númerico.")
            elif mode == "watch":
                await bot.send_message(chat_id,
                                       AUTH_USERS)
            else:
                try:
                    user_id = int(data)
                    _ui = {"user_id": user_id}
                    _c = await confirm(_u, _ui)
                    if _c:
                        await remove_(_u, _ui)
                        await bot.send_message(chat_id,
                                               f'Se elimino "{data}" de la base de datos')
                    else:
                        await bot.send_message(chat_id,
                                               f'"{user_id}" no se encuentra en la base de datos.')
                except ValueError:
                    await bot.send_message(chat_id,
                                           "El valor debe de ser númerico.")

