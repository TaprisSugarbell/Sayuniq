import shutil

from source.helpers.downloader import download_assistant
from source.helpers.site_assistant import SitesAssistant


async def database_assistant(
    anime_info: SitesAssistant, servers, anime_url, chapter_url, update: bool = None
):
    app, folder, caption, thumb_url = (
        anime_info.app,
        anime_info.folder,
        anime_info.caption,
        anime_info.thumb,
    )

    message = await download_assistant(
        app,
        servers,
        folder,
        caption,
        thumb_url,
        anime=anime_info.title,
        site=anime_info.site,
    )

    shutil.rmtree(folder)

    await anime_info.update_property(
        anime_url=anime_url,
        chapter_url=chapter_url,
        msg=message,
        message_id=message.id,
        update=update,
    )

    await anime_info.buttons_replace()
    await anime_info.update_or_add_db()
