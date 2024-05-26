import asyncio
import logging
import shutil
import time

from source.helpers.anime_sites import sites

logger = logging.getLogger(__name__)


def run_asyncio(obj, *args, **kwargs):
    asyncio.run(obj(*args, **kwargs))


async def process_site_event(site):
    start = time.time()
    try:
        await site()
    except Exception as e:
        shutil.rmtree("./downloads/", ignore_errors=True)
        logger.error(f'Failed to extract from - "{site.__name__}"', exc_info=e)
    logging.info(f"Upload completed in {round(time.time() - start)}s :3")


async def read_and_execute():
    while True:
        for site in sites:
            await process_site_event(site)
        await asyncio.sleep(120)
