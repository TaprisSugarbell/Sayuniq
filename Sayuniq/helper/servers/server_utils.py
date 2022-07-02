import json
import re
import aiohttp
from bs4 import BeautifulSoup
from .. import requests, PARSER


async def get_jk_anime(slug_title):
    async with aiohttp.ClientSession() as request:
        _url_base = "https://jkanime.net/"
        r = await request.get(
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
    r = requests.get(_url)
    soup = BeautifulSoup(r.content, PARSER)
    return soup.find("div", attrs={"class": "lista"}).find("a").get("href")
