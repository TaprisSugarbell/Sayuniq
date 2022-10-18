import asyncio
import json
import mimetypes
import os
import random
import re
import math
from typing import Any
from urllib import parse
from urllib.parse import urlparse

import aiofiles
import aiohttp
import cloudscraper
import yt_dlp as youtube_dl
from PIL import Image
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .utils import rankey
from .. import logging_stream_info
from ..__vars__ import CHANNEL_ID, LOG_CHANNEL, human_hour_readable
from ..strings import get_string

requests = cloudscraper.create_scraper(cloudscraper.Session)


class SayuDownloader:
    def __init__(self,
                 url,
                 out="./",
                 custom=None,
                 ext=None, thumb=None, _app=None, limit=20000000, filter_links=False):
        self.url = url
        self.out = out if out[-1] == "/" else f"{out}/"
        self.custom = custom
        self.ext = ext
        self.thumb = thumb
        self.app = _app
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
                print(e)
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
                soup = BeautifulSoup(_r.content, 'html.parser')
                dwnld = soup.find(id='downloadButton')
                return dwnld.get('href')
            case host if re.match(r"www\d*.zippyshare.com", host):
                u = None
                soup = BeautifulSoup(_r.content, "html.parser")
                for i in soup.find_all("script", attrs={"type": "text/javascript"}):
                    if sm := i.string:
                        if m := re.findall('/d/.*', sm):
                            namaes = re.findall(r"/[\w.]*", m[0])
                            t = math.pow(int([_f for _f in re.findall(r"\d*", sm) if _f][0]), 3) + 3
                            u = f"/d/{namaes[1][1:]}/{int(t)}{namaes[-1]}"
                            protocol = _r.url.split(".")[0]
                            if u:
                                return f"{protocol}.zippyshare.com{u}"
            case host if re.match(r"https://[\w.]*/v/[\w-]*", _r.url):
                r = self.requests.post(f"https://{host}/api/source/" + _r.url.split("/")[-1])
                return r.json()
            case host if re.match(r"www\.solidfiles\.com", host) and solidfiles:
                soup = BeautifulSoup(_r.content, "html.parser")
                fnd_dct = re.findall(r"\{\"mimetype.*}", soup.find_all("script")[-1].string)[0]
                return json.loads(fnd_dct)["downloadUrl"]
            case _:
                return _url

    async def extractor(self, url=None, solidfiles=False):
        _url, out, custom, ext, thumb = (
            url or self.url,
            self.out,
            self.custom,
            self.ext,
            self.thumb
        )
        if self.filter_links:
            _url = await self.links_filter(_url)
            if isinstance(_url, dict):
                _url = _url["data"][-1]["file"]
        if solidfiles:
            _url = await self.links_filter(_url, solidfiles)
        video_info = youtube_dl.YoutubeDL().extract_info(_url, download=False)
        # Thumbnail?
        _thumb = await self.get_thumbnail()
        # Demás datos, title, ext
        _title = re.sub("/", "", custom or video_info["title"]) + f"@{CHANNEL_ID}"
        try:
            _ext = ext or video_info["ext"]
        except KeyError:
            _ext = video_info["entries"][0]["formats"][0]["ext"]
        # Options + Download
        options = {"format": "bestaudio+bestvideo/best",
                   "outtmpl": out + _title + "." + _ext}
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
        return {
            "file": out_,
            "type": file_type,
            "thumb": yes_thumb
        }

    async def iter_links(self, urls=None, key_id=rankey(), **kwargs) -> Any:
        urls = urls or self.url
        if not isinstance(urls, list):
            return None
        _total_urls = len(urls)
        _out = None
        _reply_links = [
            [
                InlineKeyboardButton("Pause", f'pam_{key_id}'),
                InlineKeyboardButton("Pause", f'bam_{key_id}')
            ]
        ]
        for _nn, url in enumerate(urls):
            _rl_ps = urlparse(url).netloc if isinstance(url, str) else urlparse(url[0]).netloc
            _dats = dict(url=url, dif=_nn, total=_total_urls, netloc=_rl_ps,
                         date=human_hour_readable(), **kwargs)
            if self._message_id:
                await self.app.edit_message_text(
                    LOG_CHANNEL,
                    self._message_id,
                    get_string("URL_UP_LOADING").format(**_dats),
                    disable_web_page_preview=True)
            else:
                msh_ = await self.app.send_message(
                    LOG_CHANNEL, get_string("URL_UP_LOADING").format(**_dats))
                self._message_id = msh_.id
            try:
                if isinstance(url, tuple):
                    _out = await self.extractor(url[0])
                elif isinstance(url, list):
                    _out = await self.extractor(url[0], True)
                else:
                    if _rl_ps == "www.yourupload.com" and _nn != _total_urls:
                        urls.append((url,))
                        continue
                    elif _rl_ps == "www.solidfiles.com" and _nn != _total_urls:
                        urls.append([url])
                    _out = await asyncio.wait_for(self.extractor(url), 180)
            except asyncio.TimeoutError:
                urls.append((url,))
                logging_stream_info(
                    f"Fallo la descarga de - [{_nn}/{_total_urls}] - [link]({url}) por \"TimeoutError\"")
                _total_urls += 1
            except Exception as e:
                logging_stream_info(f'Fallo la descarga de {url} [{_nn}/{_total_urls}]')
                if self.thumb and os.path.exists(self.thumb):
                    os.remove(self.thumb)
                await self.app.edit_message_text(LOG_CHANNEL, self._message_id, get_string("URL_DWN_ERR").format(**_dats), disable_web_page_preview=True)

            if _out:
                await self.app.edit_message_text(
                    LOG_CHANNEL,
                    self._message_id,
                    get_string("URL_UPLOADED").format(**_dats),
                    disable_web_page_preview=True)
                break
        return _out


async def download_assistant(_app, urls, folder, caption, thumb=None, **kwargs):
    sd = SayuDownloader(urls, folder, thumb=thumb, _app=_app, filter_links=True)
    logging_stream_info(urls)
    vide_file = await sd.iter_links(**kwargs)
    file_video = vide_file["file"]
    thumb = vide_file["thumb"]
    logging_stream_info(f"Se ha descargado {vide_file}")
    # file, type, thumb
    clip = VideoFileClip(vide_file["file"])
    # Extraer información del video
    width, height = clip.size
    duration = int(clip.duration)
    match vide_file["type"]:
        case "video/mp4":
            msg_f = await _app.send_video(
                CHANNEL_ID,
                file_video,
                caption,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb
            )
            return msg_f
        case _:
            print(vide_file["type"])
            return None
