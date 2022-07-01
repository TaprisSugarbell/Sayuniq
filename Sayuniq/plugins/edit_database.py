from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .. import BOT_NAME, auth_users
from ..helper.chapters.chapters_pg import chapters_ikb
from ..helper.mongo_connect import *

db = Mongo(database=BOT_NAME, collection="japanemi")


@Client.on_message(filters.regex("mty_.*") & filters.private)
async def __edb__(bot, update):
    print(update)
    chat_id = update.from_user.id
    message_id = update.id
    AUTH_USERS = await auth_users()
    c, key_id = update.text.split()[1].split("_")
    _c = await confirm_one(db, {"key_id": key_id})
    if _c:
        site = _c["site"]
        thumb = _c["thumb"]
        anime = _c["anime"]
        chapters = _c["chapters"]
        anime_url = _c["anime_url"]
        print(_c)
        if chat_id in AUTH_USERS:
            await bot.send_message(
                chat_id,
                f'`{key_id}`\n**{anime}**\nCapítulos subidos: **{len(chapters)}**',
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Title", f'ttl_{key_id}'),
                            InlineKeyboardButton("Thumb", f'thb_{key_id}')
                        ],
                        [
                            InlineKeyboardButton("Menu ID", f'mid_{key_id}'),
                            InlineKeyboardButton("Chapters", f'chps_{key_id}')
                        ],
                        [
                            InlineKeyboardButton("Ban Anime", f'bam_{key_id}'),
                        ]
                    ]
                )
            )
        else:
            chikb = await chapters_ikb(_c)
            await bot.send_message(
                chat_id,
                message_id,
                f'**{anime}**\nCapítulos subidos: **{len(chapters)}**',
                reply_markup=chikb
            )
    else:
        await bot.send_message(chat_id, "No hay capítulos subidos...")


@Client.on_callback_query(filters.regex(r"chps_.*"))
async def __chps__(bot, update):
    print(update)
    chat_id = update.from_user.id
    c, key_id = update.data.split("_")
    _c = await confirm_one(db, {"key_id": key_id})
    site = _c["site"]
    thumb = _c["thumb"]
    anime = _c["anime"]
    chapters = _c["chapters"]
    anime_url = _c["anime_url"]
    chikb = await chapters_ikb(_c)
    await bot.send_message(
        chat_id,
        f'**{anime}**\nCapítulos subidos: **{len(chapters)}**',
        reply_markup=chikb
    )


@Client.on_callback_query(filters.regex(r"ttl_.*"))
async def __edit_title__(bot, update):
    print(update)
    chat_id = update.from_user.id
    data, key_id = update.data.split("_")
    ky_id = {
        "key_id": key_id
    }
    msg = await bot.ask(chat_id, 'Envía el nuevo titulo')
    print(msg)
    await update_one(db, ky_id, {
        "title": msg.text
    })
    await bot.send_message(chat_id, "Title updated!")
    await bot.delete_messages(chat_id, msg.request.id)


@Client.on_callback_query(filters.regex(r"thb_.*"))
async def __edit_thumb__(bot, update):
    print(update)
    chat_id = update.from_user.id
    data, key_id = update.data.split("_")
    ky_id = {
        "key_id": key_id
    }
    msg = await bot.ask(chat_id, 'Envía link o imagen')
    if getattr(msg, "photo"):
        await update_one(db, ky_id, {
            "thumb": msg.photo.file_id
        })
    else:
        await update_one(db, ky_id, {
            "thumb": msg.text
        })
    await bot.send_message(chat_id, "Thumb updated!")
    await bot.delete_messages(chat_id, msg.request.id)


@Client.on_callback_query(filters.regex(r"bam.*"))
async def __ban_anime__(bot, update):
    print(update)
    chat_id = update.from_user.id
    data, key_id = update.data.split("_")
    ky_id = {
        "key_id": key_id
    }
    _c = await confirm_one(db, ky_id)
    _tt = _c.get("is_banned")
    tre = True if _tt is False else (True if _tt is None else False)
    await update_many(db, {"anime": _c["anime"]}, {"is_banned": tre})
    if _tt:
        await bot.send_message(chat_id, f'**{_c["anime"]}** ha sido desbaneado!')
    else:
        await bot.send_message(chat_id, f'**{_c["anime"]}** ha sido baneado!')

