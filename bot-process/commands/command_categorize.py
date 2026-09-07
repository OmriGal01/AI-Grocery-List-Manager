import asyncpg
from typing import override, cast

from models.request_types import RequestType
from .command import Command
import db
from language.language_yaml_parser import LANGUAGE_REQUEST_TYPE_TO_DELIMITER
from models.item import Item

class CommandCategorize(Command):
    EMOJI = "📁"

    REQUEST_TYPE = RequestType.CATEGORIZE

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        if not isinstance(payload, Item):
            return None
        return await db.categorize_item_by_name(pool, list_id, payload.name, payload.category)

    @override
    def format_reply(self, result: object) -> str:
        if not Command.is_valid_query_result(result):
            return Command.SOMETHING_WENT_WRONG
        result = cast(dict, result)
        if all(result.values()):
            return f"{self.EMOJI} Categorized {Command.build_str_from_query_results(result)}"
        lines = [f"{self.EMOJI} Categorized {item_name}" if result[item_name]
                 else f"{Command.WARN_EMOJI} {item_name.capitalize()} was not in list"
                 for item_name in result.keys()]
        return '\n'.join(lines)

    @override
    def extract_payload(self):
        delimiter = LANGUAGE_REQUEST_TYPE_TO_DELIMITER.get(self.parsed_message.language, {}).get(self.REQUEST_TYPE)
        if not delimiter:
            return None
        arguments = self.parsed_message.first_line_item_name.split(f" {delimiter} ")
        if len(arguments) != 2:
            return None
        item_name = arguments[0].strip()
        category_name = arguments[1].strip()
        return Item(item_name, category_name)
