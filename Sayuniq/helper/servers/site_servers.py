import base64
import json
import re

import aiohttp
from bs4 import BeautifulSoup

from ... import logging_stream_info
from ...__vars__ import USER_AGENT

PARSER = "html.parser"


async def get_tioanime_servers(chapter_url):
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(chapter_url) as r:
            logging_stream_info(f"Get {chapter_url} is \"{r.ok}\"")
            soup = BeautifulSoup(await r.content.read(), PARSER)
            _script = soup.find_all("script")[-3].string
            _anime_uri = soup.find(
                "div",
                attrs={"class": "episodes-nav d-flex justify-content-center mb-4"}).find_all("a")[1].get("href")
            return re.findall(r"https?://[\w/.?#=!-]*", _script.replace("\\", "")), _anime_uri


async def get_jk_servers(chapter_url):
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(chapter_url) as r:
            logging_stream_info(f"Get {chapter_url} is \"{r.ok}\"")
            soup = BeautifulSoup(await r.content.read(), PARSER)
            _script = soup.find_all("script")
            _lnks = re.compile(r'https?://[\w./?=#-]*')
            _lks = [ie.string for ie in _script if getattr(ie, "string") and "var video = [];" in ie.string][0]
            _links = _lnks.findall(_lks.replace('src="/', 'src="https://jkanime.net/'))
            _servers = []
            for _link in _links:
                mode = _link.split("/")[3].split("?")[0]
                match mode:
                    case "um2.php":
                        _r = await session.get(
                            _link,
                            headers={
                                "referer": chapter_url
                            }
                        )
                        _soup = BeautifulSoup(
                            await _r.content.read(),
                            PARSER
                        )
                        _value = _soup.find("input").get("value")
                        _r1 = await session.post(
                            "https://jkanime.net/gsplay/redirect_post.php",
                            data={
                                "data": _value
                            },
                            headers={
                                "host": "jkanime.net",
                                "origin": "https://jkanime.net",
                                "referer": _link
                            },
                            allow_redirects=False
                        )
                        _v = _r1.headers["location"].replace("/gsplay/player.html#", "")
                        _r2 = await session.post(
                            "https://jkanime.net/gsplay/api.php",
                            data={
                                "v": _v
                            }
                        )
                        _servers.append([await _r2.json()][0]["file"])
                    case "um.php":
                        _r = await session.get(
                            _link
                        )
                        _soup = BeautifulSoup(
                            await _r.content.read(),
                            PARSER
                        )
                        _servers.append(_lnks.findall(_soup.find_all("script")[-1].string)[0])
                    case "jk.php":
                        _r = await session.get(
                            _link
                        )
                        _soup = BeautifulSoup(
                            await _r.content.read(),
                            PARSER
                        )
                        _lnk = _lnks.findall(_soup.find_all("script")[-1].string)[0]
                        _r1 = await session.get(_lnk, allow_redirects=False)
                        _servers.append(_r1.headers["location"])
                    case "jkokru.php":
                        _servers.append("https://ok.ru/videoembed/" + _link.split("u=")[-1])
                    case "jkfembed.php":
                        _servers.append("https://fembed.com/v/" + _link.split("u=")[-1])
                    case "jkvmixdrop.php":
                        _servers.append("https://mixdrop.co/e/" + _link.split("u=")[-1])
                    case _:
                        _servers.append(_link)
            return [_s for _s in _servers if _s]


async def get_mc_servers(chapter_url):
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(chapter_url) as r:
            logging_stream_info(f"Get {chapter_url} is \"{r.ok}\"")
            soup = BeautifulSoup(await r.content.read(), PARSER)
            _bb = [oei.get("data-player") for oei in
                   soup.find("div", attrs={"class": "playother"}).find_all("p")]

            b64_decoded = [oy.split("?url=")[-1] for oy in [base64.b64decode(oe).decode() for oe in _bb]]
            b64_decoded.extend(
                [ei.get("href") for ei in soup.find("div", attrs={"class": "downbtns"}).find_all("a")]
            )
            return b64_decoded


async def get_flv_servers(chapter_url):
    async with aiohttp.ClientSession(headers=USER_AGENT) as session:
        async with session.get(chapter_url) as r:
            logging_stream_info(f"Get {chapter_url} is \"{r.ok}\"")
            soup = BeautifulSoup(await r.content.read(), "html.parser")
    return [
        ou.get("code") for ou in json.loads(
            re.findall(r"\{\"SUB.*}", soup.find_all("script")[-7].string)[0])["SUB"]
    ]
