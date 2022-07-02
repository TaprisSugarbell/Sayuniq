from .downloader import download_assistant


async def database_assistant(_sa, app, servers, folder, caption,
                             thumb_url, anime_url, chapter_url, _update=None):
    msg_ = await download_assistant(app, servers, folder, caption,
                                    thumb_url, anime=_sa.title, site=_sa.site)
    await _sa.update_property(
        anime_url=anime_url,
        chapter_url=chapter_url,
        caption=caption,
        msg=msg_,
        message_id=msg_.id,
        update=_update
    )
    await _sa.buttons_replace()
    await _sa.update_or_add_db()















