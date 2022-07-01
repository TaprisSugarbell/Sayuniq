import asyncio

from __init__ import app, logs_channel_update, logging_stream_info
from __vars__ import BOT_NAME, __version__
from helper.logs_utils import sayu_error
from helper.loop_in_thread import read_and_execute, run_asyncio


async def main():
    await app.start()
    await logs_channel_update()
    await asyncio.to_thread(run_asyncio, obj=read_and_execute, app=app)

if __name__ == "__main__":
    logging_stream_info(f"Starting {BOT_NAME}, version - {__version__}")
    try:
        app.run(main())
    except Exception as e:
        app.run(sayu_error(e, app))
