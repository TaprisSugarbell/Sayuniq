import re
import string

import aiohttp
from bs4 import BeautifulSoup

import logging
from source.config import BOT_NAME, USER_AGENT
from source.helpers.servers.server_utils import get_jk_anime, get_mc_anime

from .database_utils import database_assistant
from .logs_utils import bot_error
from .mongo_connect import Mongo
from .servers import (
    get_flv_servers,
    get_jk_servers,
    get_mc_servers,
    get_tioanime_servers,
)
from source.helpers.site_assistant import SitesAssistant

logger = logging.getLogger(__name__)
db = Mongo(database=BOT_NAME, collection="japanemi")


async def tioanime(app):
    _site = "TioAnime"
    _url_base = "https://tioanime.com/"
    async with aiohttp.ClientSession() as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_animes = soup.find("ul", attrs={"class": "episodes"}).find_all("a")
            for anime in list_of_animes[::-1]:
                chapter_no = [
                    i for i in re.findall(r"[\d.]*", anime.find("h3").text) if i
                ][-1]
                title = anime.find("h3").text.replace(chapter_no, "").strip()
                chapter_url = _url_base[:-1] + anime.get("href")
                anime_info = SitesAssistant(
                    site=_site,
                    title=title,
                    thumb=None,
                    chapter_no=chapter_no,
                    database=db,
                    app=app,
                )
                in_db = await anime_info.find_on_db()
                await anime_info.get_caption()
                if in_db:
                    get_chapter = await anime_info.get_chapter()
                    if get_chapter or in_db.get("is_banned") or in_db.get("is_paused"):
                        continue
                    try:
                        servers, _anime_uri = await get_tioanime_servers(chapter_url)
                        anime_url = _url_base[:-1] + _anime_uri
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                            update=True,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)
                else:
                    servers, _anime_uri = await get_tioanime_servers(chapter_url)
                    anime_url = _url_base[:-1] + _anime_uri
                    try:
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)


async def jkanime(app):
    _site = "Jkanime"
    _url_base = "https://jkanime.net/"
    async with aiohttp.ClientSession(
        headers=USER_AGENT, timeout=aiohttp.ClientTimeout(5)
    ) as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_animes = soup.find("div", attrs={"class": "maximoaltura"}).find_all(
                "a"
            )
            for anime in list_of_animes[::-1]:
                title = anime.find("h5").string
                chapter_url = anime.get("href")
                chno = chapter_url.split("/")[-2]
                chapter_no = chno if chno[0] in string.digits else "1"
                anime_url = await get_jk_anime(title)
                _h6 = anime.find("h6").string.lower()
                extra_caption = (
                    " Final" if "final" in _h6 else (" ONA" if "ona" in _h6 else "")
                )
                anime_info = SitesAssistant(
                    site=_site,
                    title=title,
                    thumb=None,
                    chapter_no=chapter_no,
                    database=db,
                    app=app,
                )
                in_db = await anime_info.find_on_db()
                await anime_info.get_caption(extra_caption)
                if in_db:
                    get_chapter = await anime_info.get_chapter()
                    if get_chapter or in_db.get("is_banned") or in_db.get("is_paused"):
                        continue
                    try:
                        servers = await get_jk_servers(chapter_url)
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                            update=True,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)
                else:
                    servers = await get_jk_servers(chapter_url)
                    try:
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)


async def monoschinos(app):
    _site = "MonosChinos"
    _url_base = "https://monoschinos2.com/"
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(_url_base) as r:
            print(r.status)
            soup = BeautifulSoup(await r.content.read(), "html.parser")
            list_of_animes = soup.find(
                "div", attrs={"class": "row row-cols-5"}
            ).find_all("a")
            for _a in list_of_animes[::-1]:
                title = _a.find("h2", attrs={"class": "animetitles"}).string
                chapter_no = _a.find("p").string
                chapter_url = _a.get("href")
                anime_url = await get_mc_anime(chapter_url)
                anime_info = SitesAssistant(
                    site=_site,
                    title=title,
                    thumb=None,
                    chapter_no=chapter_no,
                    database=db,
                    app=app,
                )
                in_db = await anime_info.find_on_db()
                await anime_info.get_caption()
                if in_db:
                    get_chapter = await anime_info.get_chapter()
                    if get_chapter or in_db.get("is_banned") or in_db.get("is_paused"):
                        continue
                    try:
                        servers = await get_mc_servers(chapter_url)
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                            update=True,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)
                else:
                    servers = await get_mc_servers(chapter_url)
                    try:
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)


async def animeflv(app):
    _site = "AnimeFLV"
    _url_base = "https://www3.animeflv.net/"
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(_url_base) as r:
            r.status
            soup = BeautifulSoup(await r.content.read(), "html.parser")
            list_of_animes = soup.find(
                "ul", {"class": "ListEpisodios AX Rows A06 C04 D03"}
            ).find_all("a")
            for anime in list_of_animes[::-1]:
                title = anime.find("strong", attrs={"class": "Title"}).string
                chapter_no = anime.find("span", attrs={"class": "Capi"}).string.split()[
                    -1
                ]
                chapter_url = _url_base[:-1] + anime.get("href")
                anime_url = "-".join(chapter_url.split("-")[:-1]).replace(
                    "/ver/", "/anime/"
                )
                anime_info = SitesAssistant(
                    site=_site,
                    title=title,
                    thumb=None,
                    chapter_no=chapter_no,
                    database=db,
                    app=app,
                )
                in_db = await anime_info.find_on_db()
                await anime_info.get_caption()
                if in_db:
                    get_chapter = await anime_info.get_chapter()
                    if get_chapter or in_db.get("is_banned") or in_db.get("is_paused"):
                        continue
                    try:
                        servers = await get_flv_servers(chapter_url)
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                            update=True,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)
                else:
                    servers = await get_flv_servers(chapter_url)
                    try:
                        await database_assistant(
                            anime_info=anime_info,
                            servers=servers,
                            anime_url=anime_url,
                            chapter_url=chapter_url,
                            update=True,
                        )
                    except Exception as e:
                        await bot_error(error=e, app=app)


sites = [
    animeflv,
    #    jkanime,
    monoschinos,
    tioanime,
]
