from pyromod.helpers import ikb
from ...config import CHANNEL_ID
from pyrogram import Client, filters
from ..site_assistant import base_channel_url
from ..hps.pagination import Pagination


def page_data(page):
    return f"pgd_{key_id}_{page}"


def chapter_data(item, page):
    return base_channel_url(CHANNEL_ID, item["message_id"])


def chapter_title(item, page):
    return f'Capítulo {item["chapter"]}'


async def chapters_ikb(obj, index=0):
    global key_id
    key_id = obj["key_id"]
    chapters = obj["chapters"]
    chapters = [chapters[oy] for oy in sorted(chapters, key=lambda x: float(x))]
    page = Pagination(
        chapters,
        page_data=page_data,
        item_data=chapter_data,
        item_title=chapter_title,
        _type="url",
    )
    lines = 5
    columns = 3
    return ikb(page.create(index, lines, columns))
