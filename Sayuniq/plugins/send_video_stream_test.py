import aiohttp
from io import BytesIO
from .. import TESTS_CHANNEL
from pyrogram import Client, filters


@Client.on_message(filters.command(["up"]))
async def __svst__(bot, update):
    print(update)
    _orl = "https://cdn.donmai.us/original/39/27/__izayoi_sakuya_touhou__39279272c19a06b268fd40931ff29317.mp4"
    async with aiohttp.ClientSession() as request:
        async with request.get(_orl) as r:
            await bot.send_video(
                TESTS_CHANNEL,
                BytesIO(await r.content.read())
            )


