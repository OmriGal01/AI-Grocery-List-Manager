from typing import override
from models.request_types import RequestType
from .command import Command
import db
import asyncpg
from category.category_display_parser import CATEGORY_TO_EMOJI, CATEGORY_TO_ORDER
from itertools import groupby

class CommandList(Command):
    REQUEST_TYPE = RequestType.GET_LIST

    LIST_EMOJI = "🛒"
    EMPTY_EMOJI = "🤔"
    UNCATEGORIZED = "uncategorized"

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return await db.get_items(pool, list_id)

    @override
    def format_reply(self, result: object) -> str:
        if not isinstance(result, list):
            return Command.SOMETHING_WENT_WRONG
        if not result:
            return f"{self.EMPTY_EMOJI} The list is empty"
        sorted_result = sorted(result, key=lambda item: (CATEGORY_TO_ORDER[item.category], item.category or ""))
        lines = [f"{self.LIST_EMOJI} Grocery List:"]
        for category, group in groupby(sorted_result, key=lambda item: item.category):
            if not category:
                category = self.UNCATEGORIZED
            category_emoji = CATEGORY_TO_EMOJI[category]
            lines.append("")
            lines.append(category.capitalize())
            lines += [f"{category_emoji} {item.name.capitalize()}" for item in group]
        return '\n'.join(lines)