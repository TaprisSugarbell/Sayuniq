import asyncio
from Sayuniq import logging_stream_info
from Sayuniq.helper.anime_sites import *
from Sayuniq.helper.mongo_connect import *
from Sayuniq.helper.utils import create_folder

folder = create_folder(temp_folder="DBooru")
img_uploaded = Mongo(database="Sayuniq", collection="booru")


def run_asyncio(obj, app):
    asyncio.run(obj(app))


async def read_and_execute(app):
    while True:
        for site in sites:
            await site(app)
        logging_stream_info("Todo subido :3")
        await asyncio.sleep(300)
