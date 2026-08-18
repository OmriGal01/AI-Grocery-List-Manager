import os
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, Request
from RequestTypes import RequestType
from pathlib import Path
from db import get_or_create_list_id
from telegram import send_telegram_message
from language_yaml_parser import WORD_TO_REQUEST_TYPE, PREFIX_TO_REQUEST_TYPE
from ParsedMessage import ParsedMessage
from Command import Command
from CommandInvalid import CommandInvalid
from CommandHelp import CommandHelp
from CommandAdd import CommandAdd
from CommandRemove import CommandRemove
from CommandList import CommandList
from CommandSendToLLM import CommandSendToLLM

COMMAND_REGISTRY = {
    RequestType.INVALID: CommandInvalid,
    RequestType.HELP: CommandHelp,
    RequestType.ADD: CommandAdd,
    RequestType.REMOVE: CommandRemove,
    RequestType.GET_LIST: CommandList,
    RequestType.SEND_TO_LLM: CommandSendToLLM
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    app.state.db_pool = await asyncpg.create_pool(database=os.environ["DB_NAME"],
                                                  user=os.environ["DB_USER"],
                                                  password=os.environ["DB_PASSWORD"],
                                                  host=f"/cloudsql/{instance_connection_name}",
                                                  min_size=2, max_size=10)
    yield
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "I'm alive!"}

def get_command_and_parsed_message(text: str) -> tuple[Command, ParsedMessage]:
    parsed_message = ParsedMessage(
        text,
        word_to_request_type=WORD_TO_REQUEST_TYPE,
        prefix_to_request_type=PREFIX_TO_REQUEST_TYPE
    )

    if not parsed_message.first_line_words:
        return CommandInvalid(), parsed_message

    for prefix, request_type in PREFIX_TO_REQUEST_TYPE.items():
        if text.startswith(prefix):
            command_type = COMMAND_REGISTRY.get(request_type, None)
            break
    else:
        request_type = WORD_TO_REQUEST_TYPE.get(parsed_message.command_candidate, RequestType.ADD)
        command_type = COMMAND_REGISTRY.get(request_type, CommandAdd) # Default to ADD when no keyword is sent

    return command_type(), parsed_message

@app.post("/webhook")
async def webhook(request: Request):
    req_json = await request.json()
    message_text = req_json["message"]["text"]
    chat_id = req_json["message"]["chat"]["id"]

    pool = app.state.db_pool
    command, parsed_message = get_command_and_parsed_message(message_text)
    list_id = await get_or_create_list_id(pool, chat_id)
    operation_result = await command.handle(app.state.db_pool, list_id, chat_id, command.extract_payload(parsed_message))
    reply_text = command.format_reply(operation_result)
    await send_telegram_message(chat_id, reply_text)

    return {"ok": True}