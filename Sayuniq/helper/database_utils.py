import shutil

from .downloader import download_assistant


async def database_assistant(_sa, servers, anime_url, chapter_url, _update=None):
    app = _sa.app
    folder = _sa.folder
    caption = _sa.caption
    thumb_url = _sa.thumb
    msg_ = await download_assistant(app, servers, folder, caption,
                                    thumb_url, anime=_sa.title, site=_sa.site)
    shutil.rmtree(folder)
    await _sa.update_property(
        anime_url=anime_url,
        chapter_url=chapter_url,
        msg=msg_,
        message_id=msg_.id,
        update=_update
    )
    await _sa.buttons_replace()
    await _sa.update_or_add_db()















