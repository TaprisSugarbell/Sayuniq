import re
import shutil
import aiohttp
from typing import Any
from .mongo_connect import *
from bs4 import BeautifulSoup
from .downloader import SayuDownloader
from .utils import create_folder, rankey
from moviepy.editor import VideoFileClip
from ..__vars__ import BOT_NAME, BOT_ALIAS, CHANNEL_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


db = Mongo(database=BOT_NAME, collection="japanemi")


def _base_channel_url(
        channel_id: str | int,
        message_id: str | int = None
):
    message_id = message_id or ""
    if isinstance(channel_id, str):
        return f"https://t.me/{channel_id}/{message_id}"
    elif isinstance(channel_id, int):
        return f"https://t.me/c/{str(channel_id).replace('-100', '')}/{message_id}"
    else:
        return channel_id


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
                 _prev_dict: dict = None,
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
        self.prev_dict = _prev_dict
        self.prev = _prev
        self.next = _next
        self.update = _update
        self.menu_id = menu_id
        self.database = _database
        self.app = app

        self.menu_id = ""
        self.key_id = rankey()

        self.prev_chapter_digit = str(round(chapter_no)) if isinstance(
            chapter_no, float) else str(int(chapter_no) - 1)

    async def update_property(self, **kwargs):
        for i, j in kwargs.items():
            setattr(self, i, j)

    @staticmethod
    async def Ibtn(_p: bool = False, **kwargs):
        if _p:
            return InlineKeyboardButton("<<", **kwargs)
        else:
            return InlineKeyboardButton(">>", **kwargs)

    async def find_on_db(self):
        self.prev_dict = await confirm(self.database, {"site": self.site, "anime": self.site})
        return self.prev_dict

    async def get_chapter(self):
        return self.prev_dict["chapters"].get(self.chapter_no)

    async def get_prev_chapter(self):
        return self.prev_dict["chapters"].get(self.prev_chapter_digit)

    async def filter_title(self, title=None):
        title = title or self.title
        return re.sub(r"[\W\d]", "", title.replace(" ", "_"))

    async def get_caption(self):
        _filter_title = await self.filter_title()
        return f"#{_filter_title}\n💮 {self.title}\n🗂 Capítulo {self.chapter_no}\n🌐 #{self.site}"

    async def update_or_add_db(self):
        _d = {
            "key_id": self.key_id or rankey(10),
            "site": self.site,
            "anime": self.title,
            "anime_url": self.anime_url,
            "thumb": self.thumb,
            "menu_id": self.menu_id,
            "chapters": {
                self.chapter_no: {
                    "url": self.chapter_url,
                    "chapter": self.chapter_no,
                    "file_id": self.msg.video.file_id,
                    "message_id": self.message_id,
                    "nav": {
                        "prev": self.prev,
                        "next": self.next
                    }
                }
            }
        }
        if self.update:
            await update_(db, self.prev_dict, _d["chapters"])
        elif self.next:
            await update_(db,
                          self.prev_dict,
                          self.prev_dict["chapters"][self.prev_chapter_digit]["nav"].update(
                              {
                                  "prev": self.prev,
                                  "next": self.next
                              }
                          )
                          )
        else:
            await add_(db, _d)

    async def buttons_replace(self, app):
        _btns, _btns1 = [], []
        prev_message_id = self.prev_dict["message_id"]
        now_chapter = self.msg
        prev_chapter = self.prev_dict["chapters"].get(self.prev_chapter_digit)
        _prev_chapter_nav_ = prev_chapter["nav"]["prev"]
        now_chapter_message_id = now_chapter.id
        _btns.append(await self.Ibtn(True, url=_base_channel_url(CHANNEL_ID, prev_message_id)))
        if _prev_chapter_nav_:
            _btns1.append(await self.Ibtn(True, url=_base_channel_url(CHANNEL_ID, _prev_chapter_nav_)))
        _btns1.append(await self.Ibtn(url=_base_channel_url(CHANNEL_ID, now_chapter_message_id)))
        try:
            await app.edit_message_reply_markup(
                CHANNEL_ID,
                prev_message_id,
                reply_markup=InlineKeyboardMarkup(
                    [
                        _btns1,
                        [
                            InlineKeyboardButton("Site Link", url=self.chapter_url)
                        ]
                    ]
                )
            )
            await self.update_property(
                prev=_prev_chapter_nav_,
                next=now_chapter_message_id
            )
            await self.update_or_add_db()
        except Exception as e:
            print(e)
        try:
            await app.edit_message_reply_markup(
                CHANNEL_ID,
                now_chapter_message_id,
                reply_markup=InlineKeyboardMarkup(
                    [
                        _btns,
                        [
                            InlineKeyboardButton("Site Link", url=self.chapter_url)
                        ]
                    ]
                )
            )
        except Exception as e:
            print(e)


async def download_assistant(_app, urls, folder, caption, thumb=None):
    sd = SayuDownloader(urls, folder, thumb=thumb, _app=_app, filter_links=True)
    vide_file = sd.iter_links()
    # file, type, thumb
    clip = VideoFileClip(vide_file["file"])
    # Extraer información del video
    width, height = clip.size
    duration = int(clip.duration)
    match vide_file["type"]:
        case "video/mp4":
            return await _app.send_video(
                CHANNEL_ID,
                vide_file["file"],
                caption,
                duration=duration,
                width=width,
                height=height
            )
        case _:
            print(vide_file["type"])
            return None


async def get_tioanime_servers(chapter_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(chapter_url) as response:
            soup = BeautifulSoup(await response.content.read(), "html.parser")
            _script = soup.find_all("script")[-3].string
            _anime_uri = soup.find(
                "div",
                attrs={"class": "episodes-nav d-flex justify-content-center mb-4"}).find_all("a")[1].get("href")
            return re.findall(r"https?://[\w/.?#=!-]*", _script.replace("\\", "")), _anime_uri


async def tioanime(app):
    _site = "TioAnime"
    _url_base = "https://tioanime.com/"
    folder = create_folder(temp_folder=_site)
    async with aiohttp.ClientSession() as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_a = soup.find("ul", attrs={"class": "episodes"}).find_all("a")
            for _a in list_of_a[::-1]:
                chapter_url = _url_base + _a.get("href")
                thumb_url = _url_base + _a.find("img").get("src")
                chapter_no = [i for i in re.findall(r"[\d.]*", _a.find("h3").text) if i][-1]
                title = _a.find("h3").text.replace(chapter_no, "").strip()
                _sa = SitesAssistant(_site, title, thumb_url, chapter_no, _database=db)
                _c = await _sa.find_on_db()
                caption = await _sa.get_caption()
                if _c:
                    _c = _c[0]
                    get_prev_chapter = await _sa.get_prev_chapter()
                    get_chapter = await _sa.get_chapter()
                    if get_chapter:
                        continue
                    else:
                        try:
                            servers, _anime_uri = await get_tioanime_servers(chapter_url)
                            anime_url = _url_base + _anime_uri
                            msg_1 = await download_assistant(app, servers, folder, caption)
                            await _sa.update_property(
                                anime_url=anime_url,
                                message_id=msg_1.video.file_id,
                                _prev=get_prev_chapter["message_id"]
                            )
                            await _sa.buttons_replace(app)
                        except Exception as e:
                            print(e)
                else:
                    prk = rankey(10)
                    servers, _anime_uri = await get_tioanime_servers(chapter_url)
                    anime_url = _url_base + _anime_uri
                    htitle = await _sa.filter_title(title)
                    _msg_menu = await app.send_message(
                        CHANNEL_ID,
                        f"#{htitle}\n",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Listado",
                                        url=f"https://t.me/{BOT_ALIAS}?start=mty_{prk}")
                                ]
                            ]
                        )
                    )
                    try:
                        msg_ = await download_assistant(app, servers, folder, caption)
                        await _sa.update_property(
                            anime_url=anime_url,
                            msg=msg_,
                            message_id=msg_.id,
                            key_id=prk,
                            menu_id=_msg_menu
                        )
                        print(msg_)
                        await _sa.update_or_add_db()
                    except Exception as e:
                        print(e)
                        await app.delete_messages(CHANNEL_ID, _msg_menu.id)

    shutil.rmtree(folder)


sites = [tioanime]
