import shutil

from source import app
from source.helpers.downloader import count_err, download_assistant
from source.helpers.site_assistant import SitesAssistant


async def database_assistant(
    anime_info: SitesAssistant, chapter_url, get_servers, update: bool = None
):
    folder, caption, thumb_url = (
        anime_info.folder,
        anime_info.caption,
        anime_info.thumb,
    )
    servers, anime_uri = await get_servers(chapter_url)
    anime_url = anime_info.url_base[:-1] + anime_uri
    try:
        message = await download_assistant(
            app,
            servers,
            folder,
            caption,
            thumb_url,
            anime=anime_info.title,
            site=anime_info.site,
        )
    except TypeError:
        await count_err(anime_info.title, anime_info.site)
        message = None
    shutil.rmtree(folder, ignore_errors=True)
    if message:
        await anime_info.update_property(
            anime_url=anime_url,
            chapter_url=chapter_url,
            msg=message,
            message_id=message.id,
            update=update,
        )

        await anime_info.buttons_replace(app)
        await anime_info.update_or_add_db()
