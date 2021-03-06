import mimetypes
import os
import random
import re
from typing import Any
from urllib import parse

import aiofiles
import aiohttp
import cloudscraper
import yt_dlp as youtube_dl
from PIL import Image
from bs4 import BeautifulSoup
from moviepy.editor import VideoFileClip

from .utils import rankey
from .. import logging_stream_info
from ..__vars__ import CHANNEL_ID

requests = cloudscraper.create_scraper(cloudscraper.Session)


class SayuDownloader:
    def __init__(self, url, out="./", custom=None, ext=None, thumb=None, _app=None, filter_links=False):
        self.url = url
        self.out = out if out[-1] == "/" else out + "/"
        self.custom = custom
        self.ext = ext
        self.thumb = thumb
        self.app = _app
        self.filter_links = filter_links
        self.__rth = rankey()
        self.__rthumb = "{}thumb-{}.jpg"
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
        if self.thumb:
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
        else:
            return self.__rthumb.format(self.out, rankey())

    async def links_filter(self, url=None) -> str | Any:
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
                    sm = i.string
                    if sm:
                        m = re.findall('"/d/.*"', sm)
                        if m:
                            u = eval(m[0].replace("+ (", "+ str( "))
                            break
                protocol = _url.split(".")[0]
                return protocol + ".zippyshare.com" + u if u else _url
            case host if re.match(r"https://[\w.]*/v/[\w-]*", _r.url):
                r = self.requests.post(f"https://{host}/api/source/" + _r.url.split("/")[-1])
                return r.json()
            case _:
                return _url

    async def extractor(self, url=None):
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
        video_info = youtube_dl.YoutubeDL().extract_info(_url, download=False)
        # Thumbnail?
        _thumb = await self.get_thumbnail()
        # Dem??s datos, title, ext
        _title = re.sub("/", "", custom or video_info["title"])
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
            yes_thumb =  await self.generate_screenshot(out_, _thumb)
        elif os.path.exists(_thumb):
            yes_thumb = _thumb
        else:
            yes_thumb = False
        return {
            "file": out_,
            "type": file_type,
            "thumb": yes_thumb
        }

    async def iter_links(self, urls=None) -> Any:
        urls = urls or self.url
        if isinstance(urls, list):
            _total_urls = len(urls)
            _out = None
            for _nn, url in enumerate(urls):
                try:
                    _out = await self.extractor(url)
                except Exception as e:
                    logging_stream_info(f'Fallo la descarga de {url} [{_nn}/{_total_urls}]')
                    if self.thumb:
                        if os.path.exists(self.thumb):
                            os.remove(self.thumb)
                    print(e)
                if _out:
                    break
            return _out
        else:
            return None


async def download_assistant(_app, urls, folder, caption, thumb=None):
    sd = SayuDownloader(urls, folder, thumb=thumb, _app=_app, filter_links=True)
    logging_stream_info(urls)
    vide_file = await sd.iter_links()
    file_video = vide_file["file"]
    thumb = vide_file["thumb"]
    logging_stream_info(f"Se ha descargado {vide_file}")
    # file, type, thumb
    clip = VideoFileClip(vide_file["file"])
    # Extraer informaci??n del video
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
