from hydrogram import Client, filters, types

from ..config import BOT_NAME, __version__


@Client.on_message(filters.command(["start", "help"]))
async def __start__(bot: Client, message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"{BOT_NAME} {__version__}, soy el bot que gestiona @Japanemision.",
    )
