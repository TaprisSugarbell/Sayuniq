from .SAss import SitesAssistant
from .database_utils import database_assistant
from .logs_utils import sayu_error
from .mongo_connect import *
from .servers import *
from .servers.server_utils import get_jk_anime, get_mc_anime
from ..__vars__ import BOT_NAME, USER_AGENT

db = Mongo(database=BOT_NAME, collection="japanemi")


async def tioanime(app):
    _site = "TioAnime"
    _url_base = "https://tioanime.com/"
    async with aiohttp.ClientSession() as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_a = soup.find("ul", attrs={"class": "episodes"}).find_all("a")
            for _a in list_of_a[::-1]:
                chapter_no = [i for i in re.findall(r"[\d.]*", _a.find("h3").text) if i][-1]
                title = _a.find("h3").text.replace(chapter_no, "").strip()
                chapter_url = _url_base[:-1] + _a.get("href")
                _sa = SitesAssistant(_site, title, None,
                                     chapter_no, _database=db, app=app)
                _c = await _sa.find_on_db()
                await _sa.get_caption()
                if _c:
                    get_chapter = await _sa.get_chapter()
                    if get_chapter or _c.get("is_banned") or _c.get("is_paused"):
                        continue
                    else:
                        try:
                            servers, _anime_uri = await get_tioanime_servers(chapter_url)
                            anime_url = _url_base[:-1] + _anime_uri
                            await database_assistant(
                                _sa, servers, anime_url, chapter_url, True)
                        except Exception as e:
                            await sayu_error(e, app)
                else:
                    servers, _anime_uri = await get_tioanime_servers(chapter_url)
                    anime_url = _url_base[:-1] + _anime_uri
                    try:
                        await database_assistant(
                            _sa, servers, anime_url, chapter_url)
                    except Exception as e:
                        await sayu_error(e, app)


async def jkanime(app):
    _site = "Jkanime"
    _url_base = "https://jkanime.net/"
    async with aiohttp.ClientSession() as session:
        async with session.get(_url_base) as result:
            soup = BeautifulSoup(await result.content.read(), "html.parser")
            list_of_a = soup.find("div", attrs={"class": "maximoaltura"}).find_all("a")
            for _a in list_of_a[::-1]:
                title = _a.find("h5").string
                chapter_no = chapter_url.split("/")[-2]
                chapter_url = _a.get("href")
                anime_url = await get_jk_anime(title)
                _h6 = _a.find("h6").string.lower()
                extra_caption = " Final" if "final" in _h6 else (" ONA" if "ona" in _h6 else "")
                _sa = SitesAssistant(_site, title, None,
                                     chapter_no, _database=db, app=app)
                _c = await _sa.find_on_db()
                await _sa.get_caption(extra_caption)
                if _c:
                    get_chapter = await _sa.get_chapter()
                    if get_chapter or _c.get("is_banned") or _c.get("is_paused"):
                        continue
                    else:
                        try:
                            servers = await get_jk_servers(chapter_url)
                            await database_assistant(
                                _sa, servers, anime_url, chapter_url, True)
                        except Exception as e:
                            await sayu_error(e, app)
                else:
                    servers = await get_jk_servers(chapter_url)
                    try:
                        await database_assistant(
                            _sa, servers, anime_url, chapter_url)
                    except Exception as e:
                        await sayu_error(e, app)


async def monoschinos(app):
    _site = "MonosChinos"
    _url_base = "https://monoschinos2.com/"
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(_url_base) as r:
            soup = BeautifulSoup(await r.content.read(), "html.parser")
            list_of_a = soup.find("div", attrs={"class": "row row-cols-5"}).find_all("a")
            for _a in list_of_a[::-1]:
                title = _a.find("p", attrs={"class": "animetitles"}).string
                chapter_no = _a.find("h5").string
                chapter_url = _a.get("href")
                anime_url = await get_mc_anime(chapter_url)
                _sa = SitesAssistant(_site, title, None,
                                     chapter_no, _database=db, app=app)
                _c = await _sa.find_on_db()
                await _sa.get_caption()
                if _c:
                    get_chapter = await _sa.get_chapter()
                    if get_chapter or _c.get("is_banned") or _c.get("is_paused"):
                        continue
                    else:
                        try:
                            servers = await get_mc_servers(chapter_url)
                            await database_assistant(
                                _sa, servers, anime_url, chapter_url, True)
                        except Exception as e:
                            await sayu_error(e, app)
                else:
                    servers = await get_mc_servers(chapter_url)
                    try:
                        await database_assistant(
                            _sa, servers, anime_url, chapter_url)
                    except Exception as e:
                        await sayu_error(e, app)


async def animeflv(app):
    _site = "AnimeFLV"
    _url_base = "https://www3.animeflv.net/"
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(_url_base) as r:
            soup = BeautifulSoup(await r.content.read(), "html.parser")
            list_of_a = soup.find("ul", {"class": "ListEpisodios AX Rows A06 C04 D03"}).find_all("a")
            for _a in list_of_a[::-1]:
                title = _a.find("strong", attrs={"class": "Title"}).string
                chapter_no = _a.find("span", attrs={"class": "Capi"}).string.split()[-1]
                chapter_url = _url_base[:-1] + _a.get("href")
                anime_url = "-".join(chapter_url.split("-")[:-1]).replace("/ver/", "/anime/")
                _sa = SitesAssistant(_site, title, None,
                                     chapter_no, _database=db, app=app)
                _c = await _sa.find_on_db()
                await _sa.get_caption()
                if _c:
                    get_chapter = await _sa.get_chapter()
                    if get_chapter or _c.get("is_banned") or _c.get("is_paused"):
                        continue
                    else:
                        try:
                            servers = await get_flv_servers(chapter_url)
                            await database_assistant(
                                _sa, servers, anime_url, chapter_url, True)
                        except Exception as e:
                            await sayu_error(e, app)
                else:
                    servers = await get_flv_servers(chapter_url)
                    try:
                        await database_assistant(
                            _sa, servers, anime_url, chapter_url)
                    except Exception as e:
                        await sayu_error(e, app)


sites = [
    animeflv,
    jkanime,
    monoschinos,
    tioanime
]
