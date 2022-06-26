import re
import shutil
import aiohttp
from .mongo_connect import *
from bs4 import BeautifulSoup
from ..strings import get_string
from .logs_utils import sayureports
from .SAss import SitesAssistant
from .utils import create_folder, rankey
from .downloader import download_assistant
from ..__vars__ import BOT_NAME, BOT_ALIAS, CHANNEL_ID
from .. import logs_channel_update, logging_stream_info
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

db = Mongo(database=BOT_NAME, collection="japanemi")


async def get_tioanime_servers(chapter_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(chapter_url) as response:
            logging_stream_info(f"Get {chapter_url} is \"{response.ok}\"")
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
                            # msg_1 = await download_assistant(app, servers, folder, caption, thumb_url)
                            servers = ["https://cdn.donmai.us/original/39/27/__izayoi_sakuya_touhou__39279272c19a06b268fd40931ff29317.mp4"]
                            msg_1 = await download_assistant(app, servers, folder, caption, thumb_url)
                            await _sa.update_property(
                                anime_url=anime_url,
                                msg=msg_1,
                                message_id=msg_1.video.file_id,
                                _prev=get_prev_chapter["message_id"]
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


sites = [tioanime]
