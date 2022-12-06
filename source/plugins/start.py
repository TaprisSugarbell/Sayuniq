from pyrogram import Client, filters, types
from ..config import BOT_NAME, __version__


@Client.on_message(filters.command(["start", "help"]) & filters.regex(r"/\w*$"))
async def __start__(bot: Client, message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"AnimeJapanTV {__version__}, Un bot en estado de prueba que hará muchas cosas.",
    )
