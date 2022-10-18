import asyncio
import shutil
import time

from Sayuniq.helper.anime_sites import *


def run_asyncio(obj, *args, **kwargs):
    asyncio.run(obj(*args, **kwargs))


async def read_and_execute(app):
    while True:
        _start = time.time()
        for site in sites:
            try:
                await site(app)
            except Exception as e:
                shutil.rmtree("./Downloads/")
                await sayu_error(e, app, f"Fallo el extractor de - \"{site.__name__}\"")
        logging_stream_info(f"Todo subido en {round(time.time() - _start)}s :3")
        await asyncio.sleep(120)
