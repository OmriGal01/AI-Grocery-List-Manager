from typing import override
from Command import Command
from RequestTypes import RequestType
from language_yaml_parser import REQUEST_TYPE_TO_DESCRIPTION, REQUEST_TYPE_TO_WORDS, REQUEST_TYPE_TO_PREFIXES
import asyncpg

class CommandHelp(Command):
    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return None

    @override
    def format_reply(self, result: object) -> str:
        help_blocks = []
        for request_type in RequestType:
            description = REQUEST_TYPE_TO_DESCRIPTION.get(request_type)
            if not description:
                continue
            commands_and_prefixes = "/".join((REQUEST_TYPE_TO_WORDS.get(request_type, [])
                                              + REQUEST_TYPE_TO_PREFIXES.get(request_type, [])))
            block = f"{commands_and_prefixes} {description}"
            help_blocks.append(block)
        help_str = "\n\n".join(help_blocks)
        return help_str if help_str else "Nothing here yet!"