from pyrogram import Client, filters


@Client.on_message(filters.command(["eval"]))
async def __tui__(bot, update):
    print(update)
