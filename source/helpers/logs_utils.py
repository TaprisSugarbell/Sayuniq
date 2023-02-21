import sys
import traceback
from typing import Any

import pyrogram
from source.helpers.utils import rankey
from source import logs_channel_update, human_hour_readable
from source import sayu_logger
from source.config import BOT_NAME
from source.locales import get_string


def report_error(bot_name: str, extra_info: str = "", reason: Exception | str = None):

    exc_info = sys.exc_info()
    tbs = traceback.format_tb(exc_info[2])
    report_file = f"./reports/report_v{rankey()}.txt"
    text = (
        f"Disclaimer:\nEste archivo se ha subido SOLO aquí, "
        f"se registra solo el hecho del error y la fecha, "
        f"respetamos su privacidad, no puede reportar este"
        f" error si tiene algún dato confidencial aquí, "
        f"nadie verá sus datos si decide no hacerlo.\n"
    )
    text += f"--------START {bot_name} CRASH LOG--------\n"
    text += extra_info
    text += "Traceback info:\nTraceback (most recent call last):\n"
    for tb in tbs:
        text += tb
    if reason:
        sayu_logger.error(
            reason, exc_info=exc_info, extra={"hhr": human_hour_readable()}
        )
        text += f"\n\nREASON:\n{reason}\n"
    text += f"\n--------FINISH {bot_name} CRASH LOG--------\n"
    with open(report_file, "w") as wfr:
        wfr.write(text)
    return report_file


async def bot_error(
    error: Exception = None, app: pyrogram.Client = None, reason: str = None, **kwargs
):
    if reason is None:
        reason = error
    return await logs_channel_update(
        report_error(bot_name=app.me.first_name.upper(), reason=error),
        "send_document",
        caption=get_string("document_err").format(
            bot_name=BOT_NAME, reason=reason, date=human_hour_readable()
        ),
        client=app,
        **kwargs,
    )
