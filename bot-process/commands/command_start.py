from typing import override
from .command import Command
import asyncpg
from language_yaml_parser import REQUEST_TYPE_TO_WORDS
from request_types import RequestType

class CommandStart(Command):
    EMOJI = "👋"

    REQUEST_TYPE = RequestType.START

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        pass

    @override
    def format_reply(self, result: object) -> str:
        greet_line = f"{CommandStart.EMOJI} Welcome!\n  Type any one of these to see what I can do\n"
        lines = [greet_line]
        for language, request_type_to_words in REQUEST_TYPE_TO_WORDS.items():
            help_words = request_type_to_words.get(RequestType.HELP, [])
            if not help_words:
                continue
            new_line = f"{language}: {'/'.join(help_words)}"
            lines.append(new_line)
        return "\n".join(lines)