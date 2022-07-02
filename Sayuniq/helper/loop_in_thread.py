import asyncio
import shutil
import time

from Sayuniq.helper.anime_sites import *
from Sayuniq.helper.mongo_connect import *
from Sayuniq.helper.utils import create_folder

folder = create_folder(temp_folder="DBooru")
img_uploaded = Mongo(database="Sayuniq", collection="booru")


def run_asyncio(obj, app):
    asyncio.run(obj(app))


async def read_and_execute(app):
    while True:
        _start = time.time()
        for site in sites:
            try:
                await site(app)
            except Exception as e:
                shutil.rmtree("./Downloads/")
                await sayu_error(e, app)
        logging_stream_info(f"Todo subido en {round(time.time() - _start)}s :3")
        await asyncio.sleep(120)
