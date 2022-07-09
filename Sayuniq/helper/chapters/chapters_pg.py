from pyromod.helpers import ikb
from ...__vars__ import CHANNEL_ID
from pyrogram import Client, filters
from ..SAss import _base_channel_url
from ..hps.pagination import Pagination


def page_data(page):
    return f'pgd_{key_id}_{page}'


def chapter_data(item, page):
    return _base_channel_url(CHANNEL_ID, item["message_id"])


def chapter_title(item, page):
    return f'Capítulo {item["chapter"]}'


async def chapters_ikb(obj):
    global key_id
    key_id = obj["key_id"]
    chapters = obj["chapters"]
    chapters = [oy for ei, oy in chapters.items()]
    page = Pagination(
        chapters,
        page_data=page_data,
        item_data=chapter_data,
        item_title=chapter_title,
        _type="url"
    )
    index = 0
    lines = 5
    columns = 3
    return ikb(page.create(index, lines, columns))

