from typing import override, cast

from models.request_types import RequestType
from .command import Command
import db
import asyncpg

class CommandRemove(Command):
    REQUEST_TYPE = RequestType.REMOVE

    EMOJI = "🗑️"

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return await db.remove_items_by_name(pool, list_id, payload)

    @override
    def format_reply(self, result: object) -> str:
        if not Command.is_valid_query_result(result):
            return Command.SOMETHING_WENT_WRONG
        result = cast(dict, result)
        if all(result.values()):
            return f"{self.EMOJI} Removed {Command.build_str_from_query_results(result)} from the list"
        lines = [f"{self.EMOJI} Removed {item_name}" if result[item_name]
                 else f"{Command.WARN_EMOJI} {item_name.capitalize()} was not in list"
                 for item_name in result.keys()]
        return '\n'.join(lines)

    @override
    def extract_payload(self):
        item_list = self.parsed_message.get_item_list(skip_categories=True)
        item_name_list = [item.name for item in item_list]
        return item_name_list
