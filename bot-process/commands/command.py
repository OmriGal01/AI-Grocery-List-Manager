import asyncpg
from abc import ABC, abstractmethod
from parsed_message import ParsedMessage
from request_types import RequestType


class Command(ABC):
    WARN_EMOJI = "❗"
    SOMETHING_WENT_WRONG = "❓ Something went wrong"

    REQUEST_TYPE = None

    def __init__(self, parsed_message: ParsedMessage):
        self.parsed_message = parsed_message

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not isinstance(cls.REQUEST_TYPE, RequestType):
            raise TypeError(f"{cls.__name__} must define a valid request type.")

    @abstractmethod
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        pass

    @abstractmethod
    def format_reply(self, result: object) -> str:
        pass

    def extract_payload(self):
        return None

    @staticmethod
    def build_str_from_query_results(dct: dict[str, bool]) -> str:
        keys = list(dct.keys())
        if not keys:
            return ""
        if len(keys) == 1:
            return keys[0]
        return ", ".join([key for key in keys[:-1]]) + " and " + keys[-1]

    @staticmethod
    def is_valid_query_result(result: object) -> bool:
        return (isinstance(result, dict)
                and all(isinstance(key, str) for key in result.keys())
                and all(isinstance(value, bool) for value in result.values())
                and len(result) > 0)
