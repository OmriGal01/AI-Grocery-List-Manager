from typing import override
from Command import Command
from ParsedMessage import ParsedMessage
import db
import asyncpg
import os
from pathlib import Path
import logging
from mcp_types import ListToolsResult
from mcp.client._memory import InMemoryTransport
from mcp.client.session import ClientSession
from mcp_server import build_mcp_server
from google import genai
from google.genai import types

# Make sure to not log tokens sent in URLs
logging.getLogger("httpx").setLevel(logging.WARNING)

class CommandSendToLLM(Command):
    SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent / "system_prompt.txt"
    SYSTEM_PROMPT = SYSTEM_PROMPT_PATH.read_text()

    @override
    async def handle(self, pool: asyncpg.Pool, list_id: int, chat_id: int, payload) -> object:
        try:
            contents = await CommandSendToLLM._build_contents(pool, chat_id, payload)
            mcp_server = build_mcp_server(pool, list_id, chat_id, contents)
            async with InMemoryTransport(mcp_server) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    gemini_tool = CommandSendToLLM._build_gemini_tool(tools)

                    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
                    while True:
                        response = await client.aio.models.generate_content(
                            model="gemini-3.1-flash-lite",
                            contents=contents,
                            config=types.GenerateContentConfig(
                                tools=[gemini_tool],
                                system_instruction=self.SYSTEM_PROMPT
                            )
                        )
                        contents.append(response.candidates[0].content)
                        logging.info(f"function_calls: {response.function_calls}")
                        if not response.function_calls:
                            await db.clear_pending_conversation(pool, chat_id)
                            return response.text

                        for function_call in response.function_calls:
                            contents.append(await CommandSendToLLM._call_mcp_tool(session, function_call))
                            if function_call.name == "query_user":
                                return function_call.args["question"]
        except Exception:
            logging.exception("send_to_llm_failed")
            return f"LLM call failed. Please try again."

    @override
    def format_reply(self, result: object) -> str:
        if not isinstance(result, str):
            return Command.SOMETHING_WENT_WRONG
        return result

    def extract_payload(self, parsed_message: ParsedMessage):
        return parsed_message.get_prefixless_message()

    @staticmethod
    async def _build_contents(pool: asyncpg.pool.Pool, chat_id: int, payload) -> list[types.Content]:
        contents = await db.get_pending_conversation(pool, chat_id) or []
        contents = [types.Content.model_validate(content) for content in contents]
        if contents and contents[-1].parts and contents[-1].parts[-1].function_call:  # resuming from a query
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_function_response(name="query_user", response={"answer": payload})]
            ))
        else:
            contents.append(types.Content(role="user", parts=[types.Part(text=payload)]))
        return contents

    @staticmethod
    def _build_gemini_tool(tools: ListToolsResult) -> types.Tool:
        function_declarations = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters_json_schema=tool.input_schema
            )
            for tool in tools.tools
        ]
        return types.Tool(function_declarations=function_declarations)

    @staticmethod
    async def _call_mcp_tool(session: ClientSession, function_call: types.FunctionCall) -> types.Content:
        result = await session.call_tool(function_call.name, function_call.args)
        logging.info(f"tool result for {function_call.name}: {result}")
        return types.Content(
            role="user",
            parts=[types.Part.from_function_response(
                name=function_call.name,
                response=result.structured_content
            )]
        )