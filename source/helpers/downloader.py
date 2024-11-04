import asyncio
import json
import logging
import mimetypes
import os
import random
import re
from typing import Any
from urllib import parse
from urllib.parse import urlparse

import aiofiles
import aiohttp
import cloudscraper
import yt_dlp as youtube_dl
from PIL import Image
from bs4 import BeautifulSoup
from hydrogram import Client
from moviepy.editor import VideoFileClip

from source.config import CHANNEL_ID, LOG_CHANNEL, human_hour_readable, BOT_NAME
from source.helpers.mongo_connect import Mongo, confirm_one, update_one
from source.helpers.utils import rankey
from source.locales import get_string
from source.config import BOT_MODE, TESTS_CHANNEL

requests = cloudscraper.create_scraper(cloudscraper.Session)
db = Mongo(database=BOT_NAME, collection="japanemi")


async def get_file_test():
    return {"file": r"./downloads/button.mp4", "thumb": "./downloads/shogun.png", "type": "video/mp4"}


async def count_err(title, site):
    find_with = {"site": site, "anime": title}
    anime_info = await confirm_one(db, find_with)
    err = anime_info.get("err") or 0
    if err == 5:
        await update_one(db, find_with, {"is_paused": True})
    else:
        await update_one(db, find_with, {"err": err + 1})


async def streamtape(downLink: str):
    async with aiohttp.ClientSession(skip_auto_headers={}) as session:
        async with session.get(downLink) as response:
            cookies = response.cookies
            html_content = await response.text()
            soup = BeautifulSoup(html_content, "html.parser")
            video_link = "https:/" + soup.find("div", id="ideoooolink").text + "&stream=1"

            real_token = re.search(r"token=[\w_-]+", soup.find_all("script")[-8].text).group(0)
            find_fake_token = urlparse(video_link).query.split("&")[-2]
            video_link = video_link.replace(find_fake_token, real_token)
        async with session.get(
                video_link,
                headers={
                    "Accept": "*/*",
                    "Accept-Encoding": "identity;q=1, *;q=0",
                    "Accept-Language": "es-419,es;q=0.9",
                    "Connection": "keep-alive",
                    "Cookie": f"_csrf={cookies['_csrf']}; _b{cookies['_b']}",
                    "Host": "streamtape.com",
                    "Range": "bytes=0-",
                    "Referer": downLink,
                    "sec-ch-ua": 'Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "Windows",
                    "Sec-Fetch-Dest": "video",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                },
                # cookies=cookies
        ) as response:
            return response.request_info.url.__str__()


class SayuDownloader:
    def __init__(
        self,
        url: str,
        out: str = "./",
        custom: str = None,
        ext: str = None,
        thumb: str = None,
        app: Client = None,
        filter_links=False,
    ):
        self.url = url
        self.out = out if out[-1] == "/" else f"{out}/"
        self.custom = custom
        self.ext = ext
        self.thumb = thumb
        self.app = app or Client
        self.filter_links = filter_links
        self.__rth = rankey()
        self.__rthumb = "{}thumb-{}.jpg"
        self._message_id = None
        self.requests = cloudscraper.create_scraper(cloudscraper.Session)

    @staticmethod
    async def generate_screenshot(file, name: str = "./thumb.jpg"):
        clip = VideoFileClip(file)
        ss_img = int(clip.duration / random.randint(15, 30))
        frame = clip.get_frame(ss_img)
        nimage = Image.fromarray(frame)
        nimage.save(name)
        return name

    async def download_thumb(self, _th=None, _url=None):
        _th = self.__rthumb.format(self.out, rankey()) if _th is None else _th
        async with aiohttp.ClientSession() as session:
            async with session.get(self.thumb or _url) as r:
                async with aiofiles.open(_th, "wb") as af:
                    await af.write(await r.content.read())
        return _th

    async def get_thumbnail(self):
        if not self.thumb:
            return self.__rthumb.format(self.out, rankey())
        _scheme = parse.urlparse(self.thumb)
        if _scheme.scheme:
            _th = self.__rthumb.format(self.out, self.__rth)
            if os.path.exists(_th):
                _th = self.__rthumb.format(self.out, rankey())
            try:
                return await self.download_thumb(_th)
            except Exception as e:
                logging.info(e)
                return _th
        elif os.path.exists(self.thumb):
            return self.thumb
        else:
            return self.app.download_media(_scheme.path, self.out)

    async def links_filter(self, url=None, solidfiles=False) -> str | Any:
        _url = url or self.url
        _r = self.requests.get(_url, allow_redirects=True)
        host = parse.urlparse(_r.url).netloc
        match host:
            case "www.mediafire.com":
                soup = BeautifulSoup(_r.content, "html.parser")
                dwnld = soup.find(id="downloadButton")
                return dwnld.get("href")
            case "streamtape.com":
                return await streamtape(_url.replace("/e/", "/v/"))
            case host if re.match(r"www\.solidfiles\.com", host) and solidfiles:
                soup = BeautifulSoup(_r.content, "html.parser")
                fnd_dct = re.findall(
                    r"\{\"mimetype.*}", soup.find_all("script")[-1].string
                )[0]
                return json.loads(fnd_dct)["downloadUrl"]
            case host if re.match(
                r"streamwish\.to|mega\.nz|https://[\w.]*/v/[\w-]*|www\d*.zippyshare.com|hqq\.tv|"
                r"cdnplaypro\.com",
                host,
            ):
                return None
            case _:
                return _url

    async def extractor(self, url=None, solidfiles=False, dats_pck=None):
        _url, out, custom, ext, thumb = (
            url or self.url,
            self.out,
            self.custom,
            self.ext,
            self.thumb,
        )
        if self.filter_links:
            _url = await self.links_filter(_url)
            if not _url:
                return None
        elif solidfiles:
            _url = await self.links_filter(_url, solidfiles)
        video_info = youtube_dl.YoutubeDL().extract_info(_url, download=False)
        await self.app.edit_message_text(
            LOG_CHANNEL,
            self._message_id,
            get_string("URL_UP_LOADING").format(**dats_pck),
            disable_web_page_preview=True,
        )
        # Thumbnail?
        _thumb = await self.get_thumbnail()
        # Demás datos, title, ext
        _title = re.sub("/", "", custom or video_info["title"]) + "@JapanemisionRebirth"
        try:
            _ext = ext or video_info["ext"]
        except KeyError:
            _ext = video_info["entries"][0]["formats"][0]["ext"]
        # Options + Download
        options = {
            "format": "bestaudio+bestvideo/best",
            "outtmpl": out + _title + "." + _ext,
        }
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download([_url])
        # Filename
        out_ = out + _title + "." + _ext
        file_type = mimetypes.guess_type(out_)[0]
        # Si es video trata de obtener capturas
        if "video" in file_type and not os.path.exists(_thumb):
            yes_thumb = await self.generate_screenshot(out_, _thumb)
        elif os.path.exists(_thumb):
            yes_thumb = _thumb
        else:
            yes_thumb = False
        return {"file": out_, "type": file_type, "thumb": yes_thumb}

    async def iter_links(self, urls=None, **kwargs) -> Any:
        urls = urls or self.url
        if not isinstance(urls, list):
            return None
        _total_urls = len(urls)
        _out = None
        for _nn, url in enumerate(urls):
            _rl_ps = (
                urlparse(url).netloc
                if isinstance(url, str)
                else urlparse(url[0]).netloc
            )
            _dats = dict(
                url=url,
                dif=_nn,
                total=_total_urls,
                netloc=_rl_ps,
                date=human_hour_readable(),
                **kwargs,
            )
            if not self._message_id:
                msh_ = await self.app.send_message(
                    LOG_CHANNEL, get_string("URL_UP_LOADING").format(**_dats)
                )
                self._message_id = msh_.id
            try:
                if isinstance(url, tuple):
                    _out = await self.extractor(url[0])
                elif isinstance(url, list):
                    _out = await self.extractor(url[0], True)
                else:
                    if _rl_ps == "www.yourupload.com":
                        _total_urls -= 1
                        continue
                    elif _rl_ps == "www.solidfiles.com" and _nn != _total_urls:
                        urls.append([url])
                        continue
                    _out = await asyncio.wait_for(
                        self.extractor(url, False, _dats), 480
                    )
            except asyncio.TimeoutError:
                urls.append((url,))
                logging.info(
                    f'Fallo la descarga de - [{_nn}/{_total_urls}] - [link]({url}) por "TimeoutError"'
                )
                _total_urls += 1
            except Exception as e:
                logging.info(
                    f"Fallo la descarga de {url} [{_nn}/{_total_urls}]"
                )
                if self.thumb and os.path.exists(self.thumb):
                    os.remove(self.thumb)
                if _nn == _total_urls:
                    await self.app.edit_message_text(
                        LOG_CHANNEL,
                        self._message_id,
                        get_string("URL_DWN_ERR").format(**_dats),
                        disable_web_page_preview=True,
                    )

            if _out:
                await self.app.edit_message_text(
                    LOG_CHANNEL,
                    self._message_id,
                    get_string("URL_UPLOADED").format(**_dats),
                    disable_web_page_preview=True,
                )
                break
        return _out


async def download_assistant(app: Client, urls, folder, caption, thumb=None, **kwargs):
    download = SayuDownloader(urls, folder, thumb=thumb, app=app, filter_links=True)
    if BOT_MODE == "TEST":
        vide_file = await get_file_test()
        CHAN_ID = TESTS_CHANNEL
    else:
        vide_file = await download.iter_links(**kwargs)
        CHAN_ID = CHANNEL_ID
    logging.info(urls)
    file_video = vide_file["file"]
    thumb = vide_file["thumb"]
    logging.info(f"Se ha descargado {vide_file}")
    # file, type, thumb
    clip = VideoFileClip(file_video)
    # Extraer información del video
    width, height = clip.size
    duration = int(clip.duration)
    match vide_file["type"]:
        case "video/mp4":
            return await app.send_video(
                chat_id=CHAN_ID,
                video=file_video,
                caption=caption,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
            )
        case _:
            logging.info(vide_file["type"])
            return None
