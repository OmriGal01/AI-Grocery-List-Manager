import os
from typing import cast

import httpx
from RequestTypes import RequestType

SOMETHING_WENT_WRONG = "❓ Something went wrong"

async def send_telegram_message(chat_id: int, text: str):
    bot_token = os.environ["BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

def build_reply_text(request_type: RequestType, query_result: object) -> str:
    match request_type:
        case RequestType.SEND_TO_LLM:
            return cast(str, query_result)
        case RequestType.ADD:
            return _build_add_reply(cast(dict[str, bool], query_result))
        case RequestType.REMOVE:
            return _build_remove_reply(cast(dict[str, bool], query_result))
        case RequestType.GET_LIST:
            return _build_list_reply(cast(list[str], query_result))
    return _build_invalid_reply()

def _build_add_reply(query_result: dict[str, bool]) -> str:
    if len(query_result.keys()) == 0:
        return SOMETHING_WENT_WRONG
    if all(query_result.values()):
        if len(query_result.keys()) == 1:
            item_name = next(iter(query_result))
            return f"✅ Added {item_name} to list"
        return "✅ All Items Added"
    lines = [f"✅ Added {item_name}" if query_result[item_name]
             else f"❗{item_name.capitalize()} is already in the list"
             for item_name in query_result.keys()]
    return '\n'.join(lines)

def _build_remove_reply(query_result: dict[str, bool]) -> str:
    if len(query_result.keys()) == 0:
        return SOMETHING_WENT_WRONG
    if all(query_result.values()):
        if len(query_result.keys()) == 1:
            item_name = next(iter(query_result))
            return f"🗑️ Removed {item_name} from list"
        return "🗑️ All Items Removed"
    lines = [f"🗑️ Removed {item_name}" if query_result[item_name]
             else f"❗{item_name.capitalize()} was not in list"
             for item_name in query_result.keys()]
    return '\n'.join(lines)

def _build_list_reply(query_result: list[str]) -> str:
    if not query_result:
        return "🤔 The list is empty"
    lines = ["🛒 Grocery List:"] + [f"● {item_name.capitalize()}" for item_name in query_result]
    return '\n'.join(lines)

def _build_invalid_reply() -> str:
    return "🚫 Invalid operation"