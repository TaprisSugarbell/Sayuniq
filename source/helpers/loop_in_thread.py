import asyncio
import shutil
import time
import logging

from pyrogram import Client
from source.helpers.anime_sites import sites
from source.helpers.logs_utils import bot_error


def run_asyncio(obj, *args, **kwargs):
    asyncio.run(obj(*args, **kwargs))


async def read_and_execute(app: Client):
    while True:
        start = time.time()
        for site in sites:
            try:
                await site(app)
            except Exception as e:
                shutil.rmtree("./downloads/", ignore_errors=True)
                await bot_error(
                    error=e,
                    app=app,
                    reason=f'Fallo el extractor de - "{site.__name__}"',
                )
        logging.info(f"Todo subido en {round(time.time() - start)}s :3")
        await asyncio.sleep(120)
