import hmac
from typing import override
from fastapi import Request
import os

from message_sources.message_source import MessageSource

class TelegramSource(MessageSource):
    @override
    def verify(self, request: Request) -> bool:
        bot_secret_token = os.environ["TELEGRAM_WEBHOOK_SECRET"]
        received_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

        return hmac.compare_digest(bot_secret_token, received_token) if received_token else False

    @override
    def extract_message(self, body: dict) -> tuple[int, str]:
        chat_id = body["message"]["chat"]["id"]
        text = body["message"]["text"]
        return chat_id, text