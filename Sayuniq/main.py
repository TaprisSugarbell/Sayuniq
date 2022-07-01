import asyncio
import pyromod.listen
from Sayuniq.strings import get_string
from helper.logs_utils import sayureports
from __vars__ import BOT_NAME, __version__
from helper.loop_in_thread import read_and_execute, run_asyncio
from __init__ import app, logs_channel_update, logging_stream_info


async def main():
    await app.start()
    await logs_channel_update()
    await asyncio.to_thread(run_asyncio, obj=read_and_execute, app=app)

if __name__ == "__main__":
    logging_stream_info(f"Starting {BOT_NAME}, version - {__version__}")
    try:
        app.run()
        # app.run(main())
    except Exception as e:
        app.run(logs_channel_update(sayureports(reason=e), "send_document",
                                    caption=get_string("document_err").format(BOT_NAME)))
