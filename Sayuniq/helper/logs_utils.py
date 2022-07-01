import os
import sys
import traceback
from typing import Any
from Sayuniq import sayulog
from Sayuniq.__vars__ import BOT_NAME
from Sayuniq.strings import get_string
from Sayuniq import logs_channel_update, human_hour_readable


def sayureports(extra_info: str = "", reason: Any = None):
    exc_info = sys.exc_info()
    streport = traceback.format_tb(exc_info[2])
    _sc = "./sayureports/sayu-report.txt"
    _txt = f"Disclaimer:\nEste archivo se ha subido SOLO aquí, " \
           f"se registra solo el hecho del error y la fecha, " \
           f"respetamos su privacidad, no puede reportar este" \
           f" error si tiene algún dato confidencial aquí, " \
           f"nadie verá sus datos si decide no hacerlo.\n"
    _txt = f"--------START {BOT_NAME.upper()} CRASH LOG--------\n"
    _txt += extra_info
    _txt += "Traceback info:\nTraceback (most recent call last):\n"
    for _ in streport:
        _txt += _
    if reason and exc_info:
        sayulog.error(reason, exc_info=exc_info)
        _txt += f"\n\nREASON:\n{reason}\n"
    _txt += f"\n--------FINISH {BOT_NAME.upper()} CRASH LOG--------\n"
    with open(_sc, "w") as wfr:
        wfr.write(_txt)
    return _sc


async def sayu_error(e, app=None):
    return await logs_channel_update(sayureports(reason=e), "send_document",
                                     caption=get_string("document_err").format(
                                         BOT_NAME,
                                         human_hour_readable()
                                     ),
                                     _app=app
                                     )










