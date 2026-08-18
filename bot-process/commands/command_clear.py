import db
from request_types import RequestType
from .command import Command
from typing import override
import asyncpg

class CommandClear(Command):
    REQUEST_TYPE = RequestType.CLEAR

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        num_items_deleted = await db.clear_list(pool, list_id)
        return num_items_deleted

    @override
    def format_reply(self, result: object) -> str:
        if not isinstance(result, int):
            return Command.SOMETHING_WENT_WRONG
        if result == 0:
            return "List was already empty"
        return f"Deleted {result} items"