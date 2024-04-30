from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from source.config import CHANNEL_ID
from source.helpers.hps.pagination import Pagination
from source.helpers.site_assistant import base_channel_url


def btn(text, value, type="callback_data"):
    return InlineKeyboardButton(text, **{type: value})


def ikb(rows=None):
    if rows is None:
        rows = []

    lines = []
    for row in rows:
        line = []
        for button in row:
            button = (
                btn(button, button) if isinstance(button, str) else btn(*button)
            )  # InlineKeyboardButton
            line.append(button)
        lines.append(line)
    return InlineKeyboardMarkup(inline_keyboard=lines)


def chapter_data(item, page):
    return base_channel_url(CHANNEL_ID, item["message_id"])


def chapter_title(item, page):
    return f'Capítulo {item["chapter"]}'


async def chapters_ikb(obj, index=0, lines=5, columns=3):
    key_id = obj["key_id"]
    page_data = staticmethod(lambda page: f"pgd_{key_id}_{page}")
    original_chapters = obj["chapters"]
    sorted_chapters = [
        original_chapters[oy]
        for oy in sorted(original_chapters, key=lambda x: float(x))
    ]
    page = Pagination(
        sorted_chapters,
        page_data=page_data,
        item_data=chapter_data,
        item_title=chapter_title,
        callback_type="url",
    )
    return ikb(page.create(index, lines, columns))
