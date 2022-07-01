import asyncio

from Sayuniq import human_hour_readable
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
            try:
                await site(app)
            except Exception as e:
                shutil.rmtree("./Downloads/")
                await logs_channel_update(sayureports(reason=e), "send_document",
                                          caption=get_string("document_err").format(
                                              BOT_NAME,
                                              human_hour_readable()
                                          ),
                                          _app=app
                                          )
        logging_stream_info("Todo subido :3")
        await asyncio.sleep(120)
