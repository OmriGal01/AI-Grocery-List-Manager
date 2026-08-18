import asyncpg
from typing import override, cast

from request_types import RequestType
from .command import Command
import db

class CommandAdd(Command):
    EMOJI = "➕"

    REQUEST_TYPE = RequestType.ADD

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return await db.add_items(pool, list_id, payload)

    @override
    def format_reply(self, result: object) -> str:
        if not Command.is_valid_query_result(result):
            return Command.SOMETHING_WENT_WRONG
        result = cast(dict, result)
        if all(result.values()):
            return f"{self.EMOJI} Added {Command.build_str_from_query_results(result)} to the list"
        lines = [f"{self.EMOJI} Added {item_name}" if result[item_name]
                 else f"{Command.WARN_EMOJI} {item_name.capitalize()} is already in the list"
                 for item_name in result.keys()]
        return '\n'.join(lines)

    @override
    def extract_payload(self):
        return self.parsed_message.get_item_list()