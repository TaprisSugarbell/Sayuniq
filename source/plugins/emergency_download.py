import logging

from moviepy.editor import VideoFileClip
from pyrogram import Client, filters

from source.helpers.downloader import SayuDownloader
from source.helpers.utils import create_folder


@Client.on_message(filters.private & filters.regex(".*http.*"))
async def emergency_download(bot, update):
    url = update.text
    temporal_folder = create_folder()
    vide_file = await SayuDownloader(url, temporal_folder, filter_links=True, app=bot).extractor()
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
            video = await bot.send_video(
                chat_id=update.from_user.id,
                video=file_video,
                duration=duration,
                width=width,
                height=height,
                thumb=thumb,
            )
            return video
        case _:
            logging.info(vide_file["type"])
            return None
