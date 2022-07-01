import re
from datetime import datetime, timedelta, timezone
from typing import Any

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .logs_utils import sayureports
from .mongo_connect import *
from .utils import rankey
from .. import logs_channel_update, sayulog
from ..__vars__ import BOT_ALIAS, BOT_NAME, CHANNEL_ID, UTC
from ..strings import get_string


def _base_channel_url(
        channel_id: str | int,
        message_id: str | int = None
):
    message_id = message_id or ""
    if re.match(r"-\d*", channel_id):
        return f"https://t.me/c/{str(channel_id).replace('-100', '')}/{message_id}"
    else:
        return f"https://t.me/{channel_id}/{message_id}"


class SitesAssistant:
    def __init__(self,
                 _site: str = None,
                 title: str = None,
                 thumb: str = None,
                 chapter_no: str | int | float = None,
                 chapter_url: str = None,
                 anime_url: str = None,
                 msg_: Any = None,
                 message_id: int = None,
                 anime_dict: dict = None,
                 _prev: str | int = None,
                 _next: str | int = None,
                 _update: bool = None,
                 menu_id: str | int = None,
                 _database=None,
                 app=None
                 ):
        self.site = _site
        self.title = title
        self.thumb = thumb
        self.chapter_no = chapter_no
        self.chapter_url = chapter_url
        self.anime_url = anime_url
        self.msg = msg_
        self.message_id = message_id
        self.anime_dict = anime_dict
        self.prev = _prev
        self.next = _next
        self.update = _update
        self.menu_id = menu_id
        self.database = _database
        self.app = app

        self.menu_id = ""
        self.key_id = None
        self.dict_copy = dict

        self.prev_chapter_digit = str(round(chapter_no)) if isinstance(
            chapter_no, float) else str(int(chapter_no) - 1)

    @property
    async def thumbnail(self):
        return self.thumb

    async def update_property(self, **kwargs):
        for i, j in kwargs.items():
            setattr(self, i, j)

    @staticmethod
    async def Ibtn(_p: bool = False, msg_btn=None, **kwargs):
        msg_btn = "<<" if _p else msg_btn or ">>"
        if _p:
            return InlineKeyboardButton(msg_btn, **kwargs)
        else:
            return InlineKeyboardButton(msg_btn, **kwargs)

    async def find_on_db(self):
        self.anime_dict = await confirm_one(
            self.database,
            {
                "site": self.site,
                "anime": self.title
            }
        )
        if self.anime_dict:
            self.dict_copy = self.anime_dict.copy()
            self.key_id = self.anime_dict["key_id"]
            self.menu_id = self.anime_dict["menu_id"]
            self.anime_url = self.anime_dict["anime_url"]
            self.thumb = self.anime_dict["thumb"] or self.thumb
        return self.anime_dict

    async def get_chapter(self):
        return self.anime_dict["chapters"].get(self.chapter_no)

    async def get_prev_chapter(self):
        return self.anime_dict["chapters"].get(self.prev_chapter_digit)

    async def filter_title(self, title=None):
        title = title or self.title
        _clean_title = re.sub(r"_+", "_", re.sub(r"\W", "_", title))
        return _clean_title[:-1] if _clean_title[-1] == "_" else _clean_title

    async def get_caption(self, extra_ch: str = ""):
        _filter_title = await self.filter_title()
        return f"#{_filter_title}\n💮 {self.title}\n🗂 Capítulo {self.chapter_no}{extra_ch}\n🌐 #{self.site}"

    async def update_or_add_db(self):
        if ":" in UTC:
            _hours, _minutes = UTC.split(":")
        else:
            _hours, _minutes = UTC, 0
        _now = datetime.now(
            timezone(
                timedelta(
                    hours=int(_hours),
                    minutes=int(_minutes)))).strftime(get_string("format_date").format("%m"))
        _d = {
            "key_id": self.key_id or rankey(10),
            "site": self.site,
            "anime": self.title,
            "anime_url": self.anime_url,
            "thumb": self.thumb,
            "menu_id": self.menu_id,
            "datetime": _now,
            "is_banned": False,
            "chapters": {
                self.chapter_no: {
                    "url": self.chapter_url,
                    "chapter": self.chapter_no,
                    "file_id": self.msg.video.file_id,
                    "message_id": self.message_id,
                    "datetime": _now,
                    "nav": {
                        "prev": self.prev,
                        "next": None
                    }
                }
            }
        }
        if self.update:
            if self.next:
                self.anime_dict["chapters"][self.prev_chapter_digit]["nav"].update(
                    {
                        "next": self.next
                    }
                )
            self.anime_dict["chapters"].update(_d["chapters"])
            self.anime_dict.pop("_id")
            self.anime_dict.update({"datetime": _d["datetime"]})
            await update_(self.database,
                          {
                              "key_id": self.key_id
                          },
                          {
                              "chapters": self.anime_dict["chapters"]
                          }
                          )
        else:
            await add_(self.database, _d)

    async def buttons_replace(self, app=None):
        app = app or self.app
        _btns, _btns1 = [], []

        now_chapter = self.msg
        now_chapter_id = now_chapter.id
        prev_chapter = self.anime_dict["chapters"].get(self.prev_chapter_digit) if self.anime_dict else None
        _lstado = await self.Ibtn(msg_btn="Listado",
                                  url=f"https://t.me/{BOT_ALIAS}?start=mty_{self.key_id}")
        _site_button = await self.Ibtn(msg_btn="Site Link", url=self.chapter_url)

        if prev_chapter:
            prev_message_id = prev_chapter.get("message_id")
            _prev_chapter_nav_ = prev_chapter["nav"].get("prev")
            _btns.append(await self.Ibtn(True, url=_base_channel_url(CHANNEL_ID, prev_message_id)))
            if _prev_chapter_nav_:
                _btns1.append(await self.Ibtn(True, url=_base_channel_url(CHANNEL_ID, _prev_chapter_nav_)))
            _btns1.append(await self.Ibtn(url=_base_channel_url(CHANNEL_ID, now_chapter_id)))
            prev_site_button = await self.Ibtn(msg_btn="Site Link", url=prev_chapter["url"])
            try:
                await app.edit_message_reply_markup(
                    CHANNEL_ID,
                    prev_message_id,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            _btns1,
                            [
                                _lstado,
                                prev_site_button
                            ]
                        ]
                    )
                )
                await self.update_property(
                    next=now_chapter_id
                )
            except Exception as e:
                sayulog.error(f"CHANNEL_ID: {CHANNEL_ID}\n"
                              f"PrevMessageId: {prev_message_id}\n"
                              f"NowChapterId: {now_chapter_id}")
                await logs_channel_update(sayureports(reason=e), "send_document",
                                          caption=get_string("document_err").format(BOT_NAME),
                                          _app=app
                                          )
        try:
            await app.edit_message_reply_markup(
                CHANNEL_ID,
                now_chapter_id,
                reply_markup=InlineKeyboardMarkup(
                    [
                        _btns,
                        [
                            _lstado,
                            _site_button
                        ]
                    ] if _btns else [
                        [
                            _lstado,
                            _site_button
                        ]
                    ]
                )
            )
        except Exception as e:
            await logs_channel_update(sayureports(reason=e), "send_document",
                                      caption=get_string("document_err").format(BOT_NAME),
                                      _app=app
                                      )
