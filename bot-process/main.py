import os
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI, Request
from RequestTypes import RequestType
from db import add_items, remove_items, get_items, get_or_create_list_id, QueryHandler
from telegram import build_reply_text, send_telegram_message
from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession
from mcp_server import build_mcp_server
from google import genai
from google.genai import types
import logging

# Make sure to not log tokens sent in URLs
logging.getLogger("httpx").setLevel(logging.WARNING)

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

async def send_to_llm(pool: asyncpg.pool.Pool, list_id: int, payload) -> str:
    try:
        mcp_server = build_mcp_server(pool, list_id)
        async with InMemoryTransport(mcp_server) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                gemini_tool = _build_gemini_tool(tools)

                contents = [types.Content(role="user", parts=[types.Part(text=payload)])]
                client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                while True:
                    response = await client.aio.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=contents,
                        config=types.GenerateContentConfig(tools=[gemini_tool])
                    )
                    contents.append(response.candidates[0].content)
                    if not response.function_calls:
                        return response.text

                    for function_call in response.function_calls:
                        contents.append(await _call_mcp_tool(session, function_call))
    except Exception:
        logging.exception("send_to_llm_failed")
        return f"LLM call failed. Please try again."

def _build_gemini_tool(tools) -> types.Tool:
    function_declarations = [
        types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=tool.input_schema
        )
        for tool in tools.tools
    ]
    return types.Tool(function_declarations=function_declarations)

async def _call_mcp_tool(session: ClientSession, function_call) -> types.Content:
    result = await session.call_tool(function_call.name, function_call.args)
    return types.Content(
        role="user",
        parts=[types.Part.from_function_response(
            name=function_call.name,
            response=result.structured_content
        )]
    )

async def handle_invalid_request(pool: asyncpg.pool.Pool, list_id: int, payload) -> None:
    pass

@app.post("/webhook")
async def webhook(request: Request):
    req_json = await request.json()
    message_text = req_json["message"]["text"]
    chat_id = req_json["message"]["chat"]["id"]

    pool = app.state.db_pool
    request_type, payload, handler = get_request_type_payload_and_handler_dispatch(message_text)
    list_id = await get_or_create_list_id(pool, chat_id)
    operation_result = await handler(app.state.db_pool, list_id, payload)
    reply_text = build_reply_text(request_type, operation_result)
    await send_telegram_message(chat_id, reply_text)

    return {"ok": True}