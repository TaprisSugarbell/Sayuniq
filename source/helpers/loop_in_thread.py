import asyncio
import shutil
import time
import logging

from hydrogram import Client
from source.helpers.anime_sites import sites
from source.helpers.logs_utils import sayu_error


def run_asyncio(obj, *args, **kwargs):
    asyncio.run(obj(*args, **kwargs))


async def process_site_event(site, app: Client):
    start = time.time()
    try:
        await site(app)
    except Exception as e:
        shutil.rmtree("./downloads/", ignore_errors=True)
        error_message = f'Failed to extract from - "{site.__name__}"'
        await sayu_error(error=e, app=app, reason=error_message)
    logging.info(f"Upload completed in {round(time.time() - start)}s :3")
    await asyncio.sleep(120)


async def read_and_execute(app: Client):
    while True:
        for site in sites:
            await process_site_event(site, app)
