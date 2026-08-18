from typing import override
from request_types import RequestType
import asyncpg
import db
from .command import Command

class CommandClear(Command):
    REQUEST_TYPE = RequestType.CLEAR

    EMOJI = "🗑️"

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        num_items_deleted = await db.clear_list(pool, list_id)
        return num_items_deleted

    @override
    def format_reply(self, result: object) -> str:
        if not isinstance(result, int):
            return Command.SOMETHING_WENT_WRONG
        if result == 0:
            return f"{Command.WARN_EMOJI} List was already empty"
        return f"{CommandClear.EMOJI} Deleted {result} items"