import shutil
import asyncio
from .servers import *
from .mongo_connect import *
from bs4 import BeautifulSoup
from ..strings import get_string
from .SAss import SitesAssistant
from .. import logs_channel_update
from .logs_utils import sayureports
from .utils import create_folder, rankey
from .downloader import download_assistant
from .servers.server_utils import get_jk_anime
from ..__vars__ import BOT_NAME, BOT_ALIAS, CHANNEL_ID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

db = Mongo(database=BOT_NAME, collection="japanemi")


async def tioanime(app):
    _site = "TioAnime"
    _url_base = "https://tioanime.com/"
    async with aiohttp.ClientSession() as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_a = soup.find("ul", attrs={"class": "episodes"}).find_all("a")
            for _a in list_of_a[::-1]:
                folder = create_folder(_site, "")
                chapter_url = _url_base + _a.get("href")
                thumb_url = _url_base + _a.find("img").get("src").replace("//uploads", "/uploads")
                chapter_no = [i for i in re.findall(r"[\d.]*", _a.find("h3").text) if i][-1]
                title = _a.find("h3").text.replace(chapter_no, "").strip()
                _sa = SitesAssistant(_site, title, thumb_url,
                                     chapter_no, _database=db, app=app)
                _c = await _sa.find_on_db()
                caption = await _sa.get_caption()
                if _c:
                    get_prev_chapter = await _sa.get_prev_chapter()
                    get_chapter = await _sa.get_chapter()
                    if get_chapter:
                        continue
                    else:
                        try:
                            servers, _anime_uri = await get_tioanime_servers(chapter_url)
                            anime_url = _url_base + _anime_uri
                            msg_1 = await download_assistant(app, servers, folder, caption, thumb_url)
                            await _sa.update_property(
                                anime_url=anime_url,
                                chapter_url=chapter_url,
                                msg=msg_1,
                                message_id=msg_1.video.file_id,
                                prev=get_prev_chapter["message_id"],
                                update=True
                            )
                            await _sa.buttons_replace()
                            await _sa.update_or_add_db()
                        except Exception as e:
                            await logs_channel_update(sayureports(reason=e), "send_document",
                                                      caption=get_string("document_err").format(BOT_NAME),
                                                      _app=app
                                                      )
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
                        msg_ = await download_assistant(app, servers, folder, caption, thumb_url)
                        await _sa.update_property(
                            anime_url=anime_url,
                            msg=msg_,
                            message_id=msg_.id,
                            key_id=prk,
                            menu_id=_msg_menu.id,
                            chapter_url=chapter_url
                        )
                        await _sa.buttons_replace()
                        await _sa.update_or_add_db()
                    except Exception as e:
                        await logs_channel_update(sayureports(reason=e), "send_document",
                                                  caption=get_string("document_err").format(BOT_NAME),
                                                  _app=app
                                                  )
                        await app.delete_messages(CHANNEL_ID, _msg_menu.id)
                shutil.rmtree(folder)


async def jkanime(app):
    _site = "Jkanime"
    _url_base = "https://jkanime.net/"
    async with aiohttp.ClientSession() as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_a = soup.find("div", attrs={"class": "maximoaltura"}).find_all("a")
            for _a in list_of_a[::-1]:
                folder = create_folder(_site, "")
                chapter_url = _a.get("href")
                title = _a.find("h5").string
                anime_url = await get_jk_anime(title)
                chapter_no = chapter_url.split("/")[-2]
                _h6 = _a.find("h6").string.lower()
                extra_caption = " Final" if "final" in _h6 else (" ONA" if "ona" in _h6 else "")
                _sa = SitesAssistant(_site, title, None,
                                     chapter_no, _database=db, app=app)
                _c = await _sa.find_on_db()
                caption = await _sa.get_caption(extra_caption)
                if _c:
                    get_prev_chapter = await _sa.get_prev_chapter()
                    get_chapter = await _sa.get_chapter()
                    if get_chapter:
                        continue
                    else:
                        try:
                            servers = await get_jk_servers(chapter_url)
                            msg_1 = await download_assistant(app, servers, folder, caption)
                            await _sa.update_property(
                                anime_url=anime_url,
                                msg=msg_1,
                                message_id=msg_1.video.file_id,
                                prev=get_prev_chapter["message_id"],
                                update=True
                            )
                            await _sa.buttons_replace()
                            await _sa.update_or_add_db()
                        except Exception as e:
                            await logs_channel_update(sayureports(reason=e), "send_document",
                                                      caption=get_string("document_err").format(BOT_NAME),
                                                      _app=app
                                                      )
                else:
                    prk = rankey(10)
                    servers = await get_jk_servers(chapter_url)
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
                            menu_id=_msg_menu.id,
                            chapter_url=chapter_url
                        )
                        await _sa.buttons_replace()
                        await _sa.update_or_add_db()
                    except Exception as e:
                        await logs_channel_update(sayureports(reason=e), "send_document",
                                                  caption=get_string("document_err").format(BOT_NAME),
                                                  _app=app
                                                  )
                        await app.delete_messages(CHANNEL_ID, _msg_menu.id)
                shutil.rmtree(folder)

sites = [
    tioanime,
    jkanime
]
