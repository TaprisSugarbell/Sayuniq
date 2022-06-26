import re
import aiohttp
from bs4 import BeautifulSoup
from ... import logging_stream_info

PARSER = "html.parser"


async def get_tioanime_servers(chapter_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(chapter_url) as response:
            logging_stream_info(f"Get {chapter_url} is \"{response.ok}\"")
            soup = BeautifulSoup(await response.content.read(), PARSER)
            _script = soup.find_all("script")[-3].string
            _anime_uri = soup.find(
                "div",
                attrs={"class": "episodes-nav d-flex justify-content-center mb-4"}).find_all("a")[1].get("href")
            return re.findall(r"https?://[\w/.?#=!-]*", _script.replace("\\", "")), _anime_uri


async def get_jk_servers(url):
    async with aiohttp.ClientSession() as requests:
        async with requests.get(url) as r:
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
                        _r = await requests.get(
                            _link,
                            headers={
                                "referer": url
                            }
                        )
                        _soup = BeautifulSoup(
                            await _r.content.read(),
                            PARSER
                        )
                        _value = _soup.find("input").get("value")
                        _r1 = await requests.post(
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
                        _r2 = await requests.post(
                            "https://jkanime.net/gsplay/api.php",
                            data={
                                "v": _v
                            }
                        )
                        _servers.append([await _r2.json()][0]["file"])
                    case "um.php":
                        _r = await requests.get(
                            _link
                        )
                        _soup = BeautifulSoup(
                            await _r.content.read(),
                            PARSER
                        )
                        _servers.append(_lnks.findall(_soup.find_all("script")[-1].string)[0])
                    case "jk.php":
                        _r = await requests.get(
                            _link
                        )
                        _soup = BeautifulSoup(
                            await _r.content.read(),
                            PARSER
                        )
                        _lnk = _lnks.findall(_soup.find_all("script")[-1].string)[0]
                        _r1 = await requests.get(_lnk, allow_redirects=False)
                        _servers.append(_r1.headers["location"])
                    case "jkokru.php":
                        _servers.append("https://ok.ru/videoembed/" + _link.split("u=")[-1])
                    case "jkfembed.php":
                        _servers.append("https://fembed.com/v/" + _link.split("u=")[-1])
                    case "jkvmixdrop.php":
                        _servers.append("https://mixdrop.co/e/" + _link.split("u=")[-1])
                    case _:
                        _servers.append(_link)
            return _servers




