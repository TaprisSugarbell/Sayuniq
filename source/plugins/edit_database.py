from pyrogram import Client, types, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from .. import auth_users, BOT_NAME
from ..helpers.chapters.chapters_page import chapters_ikb
from ..helpers.mongo_connect import Mongo, update_one, confirm_one, update_many

db = Mongo(database=BOT_NAME, collection="japanemi")


@Client.on_message(filters.regex("mty_.*") & filters.private)
async def __edb__(bot: Client, update):

    message_id = update.id
    chat_id = update.from_user.id
    AUTH_USERS = await auth_users()
    c, key_id = update.text.split()[1].split("_")
    _c = await confirm_one(db, {"key_id": key_id})
    if _c:
        site = _c["site"]
        thumb = _c["thumb"]
        anime = _c["anime"]
        chapters = _c["chapters"]
        anime_url = _c["anime_url"]

        if chat_id in AUTH_USERS:
            await bot.send_message(
                chat_id,
                f"`{key_id}`\n**{anime}**\nCapítulos subidos: **{len(chapters)}**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Title", f"ttl_{key_id}"),
                            InlineKeyboardButton("Thumb", f"thb_{key_id}"),
                        ],
                        [
                            InlineKeyboardButton("Menu ID", f"mid_{key_id}"),
                            InlineKeyboardButton("Chapters", f"chps_{key_id}"),
                        ],
                        [
                            InlineKeyboardButton("Pause Anime", f"pam_{key_id}"),
                            InlineKeyboardButton("Ban Anime", f"bam_{key_id}"),
                        ],
                        [
                            InlineKeyboardButton("Finalizado", f"f_one_{key_id}"),
                            InlineKeyboardButton("Finalizar todos.", f"f_all_{key_id}"),
                        ],
                    ]
                ),
            )
        else:
            _c.get("status")
            chikb = await chapters_ikb(_c)
            await bot.send_message(
                chat_id,
                f"**{anime}**\nCapítulos subidos: **{len(chapters)}**",
                reply_markup=chikb,
            )
    else:
        await bot.send_message(chat_id, "No hay capítulos subidos...")
    await bot.delete_messages(chat_id, message_id)


@Client.on_callback_query(filters.regex("pgd_.*"))
async def __pgd__(bot: Client, update: types.CallbackQuery):

    message_id = update.message.id
    chat_id = update.message.from_user.id
    AUTH_USERS = await auth_users()
    c, key_id, page = update.data.split("_")
    _c = await confirm_one(db, {"key_id": key_id})
    if _c:

        chikb = await chapters_ikb(_c, int(page))
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=chikb)
    else:
        await bot.edit_message_text(
            chat_id, "No hay capítulos... El anime fue baneado probablemente."
        )


@Client.on_callback_query(filters.regex(r"chps_.*"))
async def __chps__(bot: Client, update: types.CallbackQuery):

    chat_id = update.from_user.id
    c, key_id = update.data.split("_")
    _c = await confirm_one(db, {"key_id": key_id})
    if _c:

        chapters = _c.get("chapters")
        anime = _c["anime"]
        if chapters:
            site = _c["site"]
            thumb = _c["thumb"]
            anime_url = _c["anime_url"]
            chikb = await chapters_ikb(_c)
            await bot.send_message(
                chat_id,
                f"**{anime}**\nCapítulos subidos: **{len(chapters)}**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=chikb,
            )
        else:
            _txt = "No hay capítulos subidos.\n"
            if _c.get("is_banned"):
                _txt += f'"**{anime}**" esta baneado.'
            await bot.send_message(chat_id, _txt)
    else:
        await bot.send_message(chat_id, "No existe este anime.")


@Client.on_callback_query(filters.regex(r"ttl_.*"))
async def __edit_title__(bot: Client, update: types.CallbackQuery):

    chat_id = update.from_user.id
    data, key_id = update.data.split("_")
    ky_id = {"key_id": key_id}
    msg = await bot.ask(chat_id, "Envía el nuevo titulo")

    await update_one(db, ky_id, {"title": msg.text})
    await bot.send_message(chat_id, "Title updated!")
    await bot.delete_messages(chat_id, msg.request.id)


@Client.on_callback_query(filters.regex(r"thb_.*"))
async def __edit_thumb__(bot: Client, update: types.CallbackQuery):

    chat_id = update.from_user.id
    data, key_id = update.data.split("_")
    ky_id = {"key_id": key_id}
    _c = await confirm_one(db, ky_id)
    msg = await bot.ask(chat_id, "Envía link o imagen")
    if getattr(msg, "photo"):
        await update_many(db, {"anime": _c.get("anime")}, {"thumb": msg.photo.file_id})
    else:
        await update_many(db, {"anime": _c.get("anime")}, {"thumb": msg.text})
    await bot.send_message(chat_id, "Thumb updated!")
    await bot.delete_messages(chat_id, msg.request.id)


@Client.on_callback_query(filters.regex(r"[pb]am_.*"))
async def __ban_anime__(bot: Client, update: types.CallbackQuery):

    chat_id = update.from_user.id
    data, key_id = update.data.split("_")
    ky_id = {"key_id": key_id}
    _c = await confirm_one(db, ky_id)
    _tt = _c.get("is_banned")
    tre = True if _tt is False else (True if _tt is None else False)
    _txt_inf, _chng_inf_is = (
        ("baneado" if tre else "desbaneado", {"is_banned": tre, "chapters": {}})
        if data == "bam"
        else ("pausado" if tre else "reanudado", {"is_paused": tre})
    )
    _arm_txt_inf = f'**{_c["anime"]}** ha sido {_txt_inf}!'
    await update_many(db, {"anime": _c["anime"]}, _chng_inf_is)
    if _tt:
        await bot.send_message(chat_id, _arm_txt_inf)
    else:
        await bot.send_message(chat_id, _arm_txt_inf)
