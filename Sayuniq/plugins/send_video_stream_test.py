import cv2
import aiohttp
from io import BytesIO
from .. import TESTS_CHANNEL
from pyrogram import Client, filters
from moviepy.video.io.VideoFileClip import VideoFileClip


class NamedBytesIO(BytesIO):
    def __init__(self, content: bytes, name: str) -> None:
        super().__init__(content)
        self.name = name


@Client.on_message(filters.command(["up"]))
async def __svst__(bot, update):
    print(update)
    _fmbd = "https://www.fembed.com/v/xgmqxh571yg2m03"
    async with aiohttp.ClientSession() as request:
        async with request.get(_fmbd) as r1:
            _host = r1.host
        async with request.post(f"https://{_host}/api/source/" + _fmbd.split("/")[-1]) as r:
            rspns_json = await r.json()
            _orl = rspns_json["data"][-1]["file"]
        async with request.get(_orl) as r2:
            print(r2.headers)
            print(r2.content_length)
            print(r2.request_info)
            data = cv2.VideoCapture(_orl)
            frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = int(data.get(cv2.CAP_PROP_FPS))
            seconds = int(frames / fps)
            print(seconds)
            clip = VideoFileClip(_orl)
            # Extraer información del video
            width, height = clip.size
            duration = int(clip.duration)
            print(width, height, duration)
            await bot.send_video(
                TESTS_CHANNEL,
                # NamedBytesIO(await r.content.read(), "file")
                BytesIO(await r2.content.read()),
                file_name="@Japanemision",
                duration=duration,
                width=width,
                height=height
            )

    # _orl = "https://cdn.donmai.us/original/39/27/__izayoi_sakuya_touhou__39279272c19a06b268fd40931ff29317.mp4"
    # async with aiohttp.ClientSession() as request:


