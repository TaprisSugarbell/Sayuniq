import asyncio
import logging

from hydrogram.errors import FloodWait

from source import app, logs_channel_update
from source.config import __version__, BOT_NAME
from source.helpers import configure_workdir
from source.helpers.logs_utils import sayu_error
from source.helpers.loop_in_thread import read_and_execute, run_asyncio


def handle_floodwait_exception(flood_wait_exception: FloodWait) -> None:
    """
    :param flood_wait_exception: The FloodWait exception that was raised
    :return: None

    Handle the FloodWait exception by retrying the operation after waiting for the specified duration.
    """
    while flood_wait_exception == FloodWait:
        try:
            app.run(main(flood_wait_exception.value))
        except FloodWait as current_exception:
            flood_wait_exception = current_exception
        except Exception as err:
            raise err


async def main(flood=None):
    if flood:
        logging.warning(f"sleep for {flood} seconds.")
        await asyncio.sleep(flood)
        logging.info("wake up!")
    await configure_workdir()
    await app.start()
    await logs_channel_update()
    await asyncio.to_thread(run_asyncio, obj=read_and_execute, app=app)


if __name__ == "__main__":
    logging.info(f"Starting {BOT_NAME}, version - {__version__}")
    try:
        app.run(main())
    except FloodWait as e:
        handle_floodwait_exception(e)
    except Exception as e:
        app.run(sayu_error(e, app))
