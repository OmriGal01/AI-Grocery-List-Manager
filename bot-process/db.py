from typing import Protocol
import asyncpg

class QueryHandler(Protocol):
    async def __call__(self, pool: asyncpg.pool.Pool, list_id: int, payload):
        ...

async def get_or_create_list_id(pool: asyncpg.pool.Pool, chat_id: int) -> int:
    async with pool.acquire() as connection:
        result_id = await connection.fetchval("SELECT list_id FROM chats WHERE chat_id = $1", chat_id)
        if not result_id:
            result_id = await connection.fetchval("INSERT INTO lists DEFAULT VALUES RETURNING id")
            await connection.execute("INSERT INTO chats (chat_id, list_id) VALUES ($1, $2)", chat_id, result_id)
        return result_id

async def add_items(pool: asyncpg.pool.Pool, list_id: int, item_names: list[str]) -> dict[str, bool]:
    query = "INSERT INTO items(list_id, item_name) VALUES ($1, $2) ON CONFLICT (list_id, item_name) DO NOTHING"
    return await _run_per_item_query(pool, list_id, item_names, query)

async def remove_items(pool: asyncpg.pool.Pool, list_id: int, item_names: list[str]) -> dict[str, bool]:
    query = "DELETE FROM items WHERE list_id = $1 AND item_name = $2"
    return await _run_per_item_query(pool, list_id, item_names, query)

async def get_items(pool: asyncpg.pool.Pool, list_id: int, payload) -> list[str]:
    async with pool.acquire() as connection:
        result_records = await connection.fetch("SELECT item_name FROM items WHERE list_id = $1", list_id)
    return [row["item_name"] for row in result_records]

async def _run_per_item_query(pool: asyncpg.pool.Pool, list_id: int, item_names: list[str], query: str) -> dict[str, bool]:
    query_results = {item_name: False for item_name in item_names}
    async with pool.acquire() as connection:
        for item_name in item_names:
            result = await connection.fetchval(f"{query} RETURNING item_name", list_id, item_name)
            if result is not None:
                query_results[item_name] = True
    return query_results