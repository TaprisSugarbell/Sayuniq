import asyncio
import logging

from hydrogram.errors import FloodWait

from source import app
from source.config import BOT_NAME, __version__
from source.helpers.loop_in_thread import read_and_execute


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
        logging.warning(f"Sleeping for {flood} seconds.")
        await asyncio.sleep(flood)
        logging.info("Wake up!")
    await app.start()
    uploader_task = asyncio.create_task(read_and_execute())
    try:
        await asyncio.gather(
            uploader_task,
            return_exceptions=True
        )
    except Exception as e:
        logging.error("Error - ", exc_info=e)


if __name__ == "__main__":
    logging.info(f"Starting {BOT_NAME}, version - {__version__}")
    try:
        app.run(main())
    except SystemExit:
        logging.info("Bye!")
    except FloodWait as e:
        handle_floodwait_exception(e)
    except Exception as e:
        logging.error("Error - ", exc_info=e)
