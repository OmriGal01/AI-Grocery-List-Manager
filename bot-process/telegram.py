import os
import httpx

ERROR_EMOJI = "🚫"

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

