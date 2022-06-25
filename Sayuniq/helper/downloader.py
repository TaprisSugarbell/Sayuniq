import os
import re
import wget
import random
import string
import mimetypes
import cloudscraper
from PIL import Image
from typing import Any
from urllib import parse
from .utils import rankey
import yt_dlp as youtube_dl
from bs4 import BeautifulSoup
from .. import logging_stream_info
from moviepy.editor import VideoFileClip

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
    def generate_screenshot(file, name: str = "./thumb.jpg"):
        clip = VideoFileClip(file)
        ss_img = int(clip.duration / random.randint(15, 30))
        frame = clip.get_frame(ss_img)
        nimage = Image.fromarray(frame)
        nimage.save(name)
        return name

    def get_thumbnail(self):
        if self.thumb:
            _scheme = parse.urlparse(self.thumb)
            if _scheme.scheme:
                _th = self.__rthumb.format(self.out, self.__rth)
                if os.path.exists(_th):
                    _th = self.__rthumb.format(self.out, rankey())
                return wget.download(self.thumb, _th)
            elif os.path.exists(self.thumb):
                return self.thumb
            else:
                return self.app.download_media(_scheme.path, self.out)
        else:
            return self.__rthumb.format(self.out, rankey())

    def links_filter(self, url=None) -> str | Any:
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

    def extractor(self, url=None):
        _url, out, custom, ext, thumb = (
            url or self.url,
            self.out,
            self.custom,
            self.ext,
            self.thumb
        )
        if self.filter_links:
            _url = self.links_filter(_url)
            if isinstance(_url, dict):
                _url = _url["data"][-1]
        video_info = youtube_dl.YoutubeDL().extract_info(_url, download=False)
        # Thumbnail?
        _thumb = self.get_thumbnail()
        # Demás datos, title, ext
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
            yes_thumb = self.generate_screenshot(out_, _thumb)
        elif os.path.exists(_thumb):
            yes_thumb = _thumb
        else:
            yes_thumb = False
        return {
            "file": out_,
            "type": file_type,
            "thumb": yes_thumb
        }

    def iter_links(self, urls=None) -> Any:
        urls = urls or self.url
        if isinstance(urls, list):
            _total_urls = len(urls)
            _out = None
            for _nn, url in enumerate(urls):
                try:
                    _out = self.extractor(url)
                except Exception as e:
                    logging_stream_info(f'Fallo la descarga de {url} [{_nn}/{_total_urls}]')
                    print(e)
                if _out:
                    break
            return _out
        else:
            return None
