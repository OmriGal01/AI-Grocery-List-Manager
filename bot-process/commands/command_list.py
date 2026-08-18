from typing import override

from request_types import RequestType
from .command import Command
import db
import asyncpg

class CommandList(Command):
    REQUEST_TYPE = RequestType.GET_LIST

    LIST_EMOJI = "🛒"
    EMPTY_EMOJI = "🤔"

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return await db.get_items(pool, list_id)

    @override
    def format_reply(self, result: object) -> str:
        if not isinstance(result, list):
            return Command.SOMETHING_WENT_WRONG
        if not result:
            return f"{self.EMPTY_EMOJI} The list is empty"
        lines = [f"{self.LIST_EMOJI} Grocery List:"] + [f"● {item_name.capitalize()}" for item_name in result]
        return '\n'.join(lines)