import re
from datetime import datetime, timedelta, timezone
from typing import Any

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .logs_utils import sayu_error
from .mongo_connect import *
from .utils import rankey, create_folder
from .. import sayulog, human_hour_readable
from ..__vars__ import BOT_ALIAS, CHANNEL_ID, UTC, _base_channel_url
from ..strings import get_string


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

        self.key_id = None or rankey(10)
        self.caption = ""
        self.folder = create_folder(self.site, "")
        self.dict_copy = dict
        self.last_chapter = None

        self.prev_chapter_digit = str(
            round(chapter_no)) if isinstance(
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
            self.anime_url = self.anime_dict["anime_url"]
            self.last_chapter = self.anime_dict.get("last_chapter")
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
        self.caption = f"#{_filter_title}\n💮 {self.title}\n" \
                       f"🗂 Capítulo {self.chapter_no}{extra_ch}\n🌐 #{self.site}"
        return self.caption

    async def buttons_replace(self, app=None):
        app = app or self.app
        _btns, _btns1 = [], []

        now_chapter = self.msg
        now_chapter_id = now_chapter.id
        prev_chapter = self.anime_dict["chapters"].get(self.prev_chapter_digit) if self.anime_dict else {}
        _lstado = await self.Ibtn(msg_btn="Listado",
                                  url=f"https://t.me/{BOT_ALIAS}?start=mty_{self.key_id}")
        _site_button = await self.Ibtn(msg_btn="Site Link", url=self.chapter_url)

        if prev_chapter and float(prev_chapter.get("chapter")) < float(self.chapter_no) \
                and self.last_chapter == prev_chapter.get("chapter"):
            prev_message_id = prev_chapter.get("message_id")
            self.prev, self.next = prev_message_id, now_chapter_id
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
                              f"NowChapterId: {now_chapter_id}",
                              extra={"hhr": human_hour_readable()})
                await sayu_error(e, app)
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
            await sayu_error(e, app)

    async def update_or_add_db(self):
        _hours, _minutes = UTC.split(":") if ":" in UTC else (UTC, 0)
        _now = datetime.now(
            timezone(
                timedelta(
                    hours=int(_hours),
                    minutes=int(_minutes)))).strftime(get_string("format_date").format("%m"))
        _d = {
            "key_id": self.key_id,
            "site": self.site,
            "anime": self.title,
            "anime_url": self.anime_url,
            "thumb": self.thumb,
            "datetime": _now,
            "is_paused": False,
            "is_banned": False,
            "last_chapter": self.chapter_no,
            "chapters": {
                self.chapter_no: {
                    "url": self.chapter_url,
                    "chapter": self.chapter_no,
                    "caption": self.caption,
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
                        "prev": self.prev,
                        "next": self.next
                    }
                )
            self.anime_dict["chapters"].update(_d["chapters"])
            self.anime_dict.pop("_id")
            self.anime_dict.update({"datetime": _d["datetime"]})
            await update_one(self.database,
                             {
                                 "key_id": self.key_id
                             },
                             {
                                 "last_chapter": self.chapter_no
                             }
                             )
            await update_one(self.database,
                             {
                                 "key_id": self.key_id
                             },
                             {
                                 "chapters": self.anime_dict["chapters"]
                             }
                             )
        else:
            await add_(self.database, _d)
