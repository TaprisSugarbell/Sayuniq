from pyrogram import Client, filters
from ..__vars__ import BOT_NAME, __version__


@Client.on_message(filters.command(["start", "help"]) & filters.regex(r"/\w*$"))
async def __start__(bot, update):
    print(update)
    chat_id = update.from_user.id
    await bot.send_message(
        chat_id,
        f'**{BOT_NAME}**\n'
        f'**__version:__** {__version__}\n'
        f'Un bot en estado de prueba que hará muchas cosas.'
    )












