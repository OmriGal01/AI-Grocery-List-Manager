import os
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, Request
from RequestTypes import RequestType
from db import add_items, remove_items, get_items, get_or_create_list_id, QueryHandler

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

def get_request_type_payload_and_handler_dispatch(text: str) -> tuple[RequestType, list[str] | str | None, QueryHandler]:
    text = text.strip().lower()
    if not text:
        return RequestType.INVALID, None, handle_invalid_request
    split_text = text.split()

    if text.startswith(RequestType.SEND_TO_LLM.value):
        return RequestType.SEND_TO_LLM, text[1:], send_to_llm
    if split_text[0] in RequestType:
        request_type = RequestType(split_text[0])
        payload = split_text[1:] if request_type != RequestType.GET_LIST else None
        handler = handle_invalid_request
        match request_type:
            case RequestType.ADD:
                handler = add_items
            case RequestType.REMOVE:
                handler = remove_items
            case RequestType.GET_LIST:
                handler = get_items
        return request_type, payload, handler

    return RequestType.INVALID, None, handle_invalid_request

async def send_to_llm(pool: asyncpg.pool.Pool, list_id: int, payload) -> object:
    # TODO: Implement
    pass

async def handle_invalid_request(pool: asyncpg.pool.Pool, list_id: int, payload) -> object:
    # TODO: Choose what to do here
    return False

@app.post("/webhook")
async def webhook(request: Request):
    req_json = await request.json()
    message_text = req_json["message"]["text"]
    chat_id = req_json["message"]["chat"]["id"]

    pool = app.state.db_pool
    request_type, payload, handler = get_request_type_payload_and_handler_dispatch(message_text)
    list_id = await get_or_create_list_id(pool, chat_id)
    await handler(app.state.db_pool, list_id, payload)

    # TODO: send response to user if query was successful or not

    return {"ok": True}