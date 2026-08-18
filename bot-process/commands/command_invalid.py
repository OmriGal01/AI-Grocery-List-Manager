from typing import override

from request_types import RequestType
from .command import Command
import asyncpg

class CommandInvalid(Command):
    REQUEST_TYPE = RequestType.INVALID

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return Command.SOMETHING_WENT_WRONG

    @override
    def format_reply(self, result: object) -> str:
        return Command.SOMETHING_WENT_WRONG