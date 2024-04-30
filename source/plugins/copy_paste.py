import asyncio

from hydrogram import Client, filters, types

from source import BOT_NAME
from source.helpers.mongo_connect import (Mongo, add_one, confirm_one,
                                          remove_one, update_one)

db = Mongo(database=BOT_NAME, collection="copy_paste")


@Client.on_message(filters.command(["copy", "paste", "clear"]))
async def __copy_paste__(bot: Client, message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    reply_to_message = getattr(message, "reply_to_message")
    sender_chat = getattr(message.reply_to_message, "sender_chat")
    find_media_group_id = getattr(message.reply_to_message, "media_group_id")
    if "clear" in message.text:
        await remove_one(db, {"user_id": user_id})
        await bot.send_message(chat_id, "Se ha limpiado el texto anterior :3.")
    elif reply_to_message or find_media_group_id:
        if "copy" in message.text:
            if find_media_group_id:
                if sender_chat:
                    media_group = await bot.get_media_group(
                        sender_chat.id, message.reply_to_message_id
                    )
                else:
                    media_group = await bot.get_media_group(
                        chat_id, message.reply_to_message_id
                    )
                copy_text = [
                    msg.caption for msg in media_group if getattr(msg, "caption")
                ][0]
            else:
                copy_text = reply_to_message.text
            user = await confirm_one(
                db,
                {
                    "user_id": user_id,
                },
            )
            if user:
                if copy_text == user["copy_text"]:
                    await bot.send_message(chat_id, "Ya copiaste este texto :3")
                else:
                    await bot.send_message(
                        chat_id,
                        f"Ya haz copiado un texto, se reemplazara el anterior :3\n"
                        f"**Anterior:** `{user['copy_text']}`",
                    )
                    await update_one(db, {"user_id": user_id}, {"copy_text": copy_text})
            else:
                await add_one(db, {"user_id": user_id, "copy_text": copy_text})
                await bot.send_message(chat_id, "Se ha copiado el texto :3")
        else:
            user = await confirm_one(db, {"user_id": user_id})
            copy_text = user["copy_text"]

            if sender_chat:
                await bot.edit_message_caption(
                    sender_chat.id, reply_to_message.forward_from_message_id, copy_text
                )
            else:
                await bot.edit_message_caption(
                    chat_id, message.reply_to_message_id, copy_text
                )
            # await bot.copy_media_group(
            #     chat_id,
            #     chat_id,
            #     update.reply_to_message_id,
            #     copy_text
            # )
    else:
        await bot.send_message(chat_id, "Tienes que responder a un album.")
    await asyncio.sleep(60)
    await bot.delete_messages(chat_id, message.id)
