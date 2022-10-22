import asyncio
import logging
from source import app, logs_channel_update
from source.config import __version__
from source.helpers import configure_workdir
from source.helpers.logs_utils import bot_error
from source.helpers.loop_in_thread import read_and_execute, run_asyncio


async def main():
    await configure_workdir()
    await app.start()
    await logs_channel_update()
    await asyncio.to_thread(run_asyncio, obj=read_and_execute, app=app)


if __name__ == "__main__":
    logging.info(f"Starting Sayuniq, version - {__version__}")
    try:
        app.run(main())
    except Exception as e:
        app.run(bot_error(e, app))
