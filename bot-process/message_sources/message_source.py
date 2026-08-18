from abc import ABC, abstractmethod
from fastapi import Request

class MessageSource(ABC):
    @abstractmethod
    def verify(self, request: Request) -> bool:
        ...

    @abstractmethod
    def extract_message(self, body: dict) -> tuple[int, str]:
        ...