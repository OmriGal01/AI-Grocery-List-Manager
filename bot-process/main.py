import os
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, Request, HTTPException

import telegram
from db import get_or_create_list_id
from message_sources import MessageSource, telegram_source
from request_types import RequestType
from language_yaml_parser import FLAT_WORD_TO_REQUEST_TYPE, FLAT_PREFIX_TO_REQUEST_TYPE, WORD_TO_LANGUAGE
from parsed_message import ParsedMessage
from commands import COMMAND_REGISTRY, Command

@asynccontextmanager
async def lifespan(app: FastAPI):
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    app.state.db_pool = await asyncpg.create_pool(
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=f"/cloudsql/{instance_connection_name}",
        min_size=2, max_size=10
    )
    yield
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)

def get_command(text: str) -> Command:
    parsed_message = ParsedMessage(
        text,
        word_to_request_type_map=FLAT_WORD_TO_REQUEST_TYPE,
        prefix_to_request_type_map=FLAT_PREFIX_TO_REQUEST_TYPE,
        word_to_langauge_map=WORD_TO_LANGUAGE
    )

    command_type = COMMAND_REGISTRY.get(parsed_message.request_type, COMMAND_REGISTRY[RequestType.INVALID])

    return command_type(parsed_message)

async def process_message(request: Request, message_source: MessageSource):
    if not message_source.verify(request):
        raise HTTPException(status_code=403)
    body = await request.json()
    chat_id, message_text = message_source.extract_message(body)

    pool = app.state.db_pool
    command = get_command(message_text)
    list_id = await get_or_create_list_id(pool, chat_id)
    operation_result = await command.handle(
        pool,
        list_id,
        chat_id,
        command.extract_payload()
    )

    reply_text = command.format_reply(operation_result)
    return chat_id, reply_text

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    chat_id, reply_text = await process_message(request, telegram_source)
    await telegram.send_telegram_message(chat_id, reply_text)

    return {"ok": True}

@app.get("/")
def read_root():
    return {"status": "I'm alive!"}