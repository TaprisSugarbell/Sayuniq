import json
import re

import aiohttp
from bs4 import BeautifulSoup

PARSER = "html.parser"


async def get_jk_anime(slug_title):
    async with aiohttp.ClientSession() as requests:
        _url_base = "https://jkanime.net/"
        r = await requests.get(
            "https://jkanime.net/ajax/ajax_search/",
            params={
                "q": slug_title
            }
        )
        animes = json.loads(await r.content.read())
        for anime in animes["animes"]:
            anime_slug = anime.get("slug")
            anime_title = anime.get("title")

            match anime_title:
                case anime_title if re.findall(rf"{slug_title.lower()}", anime["title"].lower()):
                    return f"{_url_base}{anime_slug}/"
                case _:
                    continue


async def get_mc_anime(_url):
    async with aiohttp.ClientSession() as requests:
        async with requests.get(_url) as r:
            soup = BeautifulSoup(await r.content.read(), PARSER)
            return soup.find("div", attrs={"class": "lista"}).find("a").get("href")
