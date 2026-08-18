from typing import override
from Command import Command
import asyncpg

class CommandInvalid(Command):
    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        return Command.SOMETHING_WENT_WRONG

    @override
    def format_reply(self, result: object) -> str:
        return Command.SOMETHING_WENT_WRONG