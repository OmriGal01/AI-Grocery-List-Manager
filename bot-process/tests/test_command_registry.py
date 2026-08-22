import pytest
from typing import override
import asyncpg
from commands import Command, COMMAND_REGISTRY
from request_types import RequestType

def test_every_request_type_has_registered_command_type():
    for request_type in RequestType:
        assert request_type in COMMAND_REGISTRY

def test_missing_request_type_raises_error():
    with pytest.raises(TypeError):
        class CommandMissingRequestType(Command):
            @override
            async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
                pass
            @override
            def format_reply(self, result: object) -> str:
                return ""

def test_no_duplicate_command_types():
    request_types = [cls.REQUEST_TYPE for cls in Command.__subclasses__()]
    assert len(request_types) == len(set(request_types))