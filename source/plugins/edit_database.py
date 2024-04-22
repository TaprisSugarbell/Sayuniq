from hydrogram import Client, filters, types
from hydrogram.enums import ParseMode
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from source import BOT_NAME, auth_users
from source.helpers.chapters.chapters_page import chapters_ikb
from source.helpers.mongo_connect import Mongo, confirm_one, update_many, update_one
import sys
import traceback
db = Mongo(database=BOT_NAME, collection="japanemi")


@Client.on_message(filters.regex(r"mty_.*") & filters.private)
async def __edb__(bot, update):
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
        print(_c)
        if chat_id in AUTH_USERS:
            await bot.send_message(
                chat_id,
                f"`{key_id}`\n**{anime}**\nCapitulos subidos: **{len(chapters)}**",
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
                            InlineKeyboardButton(
                                "Pause Anime (one)", f"pam_{key_id}_one"
                            ),
                            InlineKeyboardButton(
                                "Ban Anime (one)", f"bam_{key_id}_one"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                "Pause Anime (all)", f"pam_{key_id}_all"
                            ),
                            InlineKeyboardButton(
                                "Ban Anime (all)", f"bam_{key_id}_all"
                            ),
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
            try:
                chikb = await chapters_ikb(_c)
            except Exception as e:
                print(traceback.format_tb(sys.exc_info()[2]))
            await bot.send_message(
                chat_id,
                f"**{anime}**\nCapitulos subidos: **{len(chapters)}**",
                reply_markup=chikb,
            )
    else:
        await bot.send_message(chat_id, "No hay capitulos subidos...")
    await bot.delete_messages(chat_id, message_id)


@Client.on_callback_query(filters.regex("pgd_.*"))
async def __pgd__(bot: Client, callback: types.CallbackQuery):
    message_id = callback.message.id
    chat_id = callback.message.from_user.id
    AUTH_USERS = await auth_users()
    c, key_id, page = callback.data.split("_")
    _c = await confirm_one(db, {"key_id": key_id})
    if _c:

        chikb = await chapters_ikb(_c, int(page))
        await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=chikb)
    else:
        await bot.edit_message_text(
            chat_id, message_id, "No hay capítulos... El anime fue baneado probablemente."
        )


@Client.on_callback_query(filters.regex(r"chps_.*"))
async def __chps__(bot: Client, callback: types.CallbackQuery):

    chat_id = callback.from_user.id
    _, key_id = callback.data.split("_")
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
async def __edit_title__(bot: Client, callback: types.CallbackQuery):

    chat_id = callback.from_user.id
    data, key_id = callback.data.split("_")
    ky_id = {"key_id": key_id}
    msg = await bot.ask(chat_id, "Envía el nuevo titulo")

    await update_one(db, ky_id, {"title": msg.text})
    await bot.send_message(chat_id, "Title updated!")
    await bot.delete_messages(chat_id, msg.request.id)


@Client.on_callback_query(filters.regex(r"thb_.*"))
async def __edit_thumb__(bot: Client, callback: types.CallbackQuery):

    chat_id = callback.from_user.id
    data, key_id = callback.data.split("_")
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
async def __ban_anime__(bot, update):
    chat_id = update.from_user.id
    data, key_id, __type__ = update.data.split("_")
    ky_id = {"key_id": key_id}
    _c = await confirm_one(db, ky_id)
    _tt = _c.get("is_banned") or _c.get("is_paused")
    tre = _tt is None if _tt else True
    _txt_inf, _chng_inf_is = (
        ("baneado" if tre else "desbaneado", {"is_banned": tre, "chapters": {}})
        if data == "bam"
        else ("pausado" if tre else "reanudado", {"is_paused": tre})
    )
    _arm_txt_inf = f'**{_c["anime"]}** ha sido {_txt_inf}!'
    match __type__:
        case "one":
            await update_one(db, ky_id, _chng_inf_is)
        case "all":
            await update_many(db, {"anime": _c["anime"]}, _chng_inf_is)
    await bot.send_message(chat_id, _arm_txt_inf)
