import json
import asyncpg
from models.item import Item

async def get_or_create_list_id(pool: asyncpg.pool.Pool, chat_id: int) -> int:
    async with pool.acquire() as connection:
        result_id = await connection.fetchval("SELECT list_id FROM chats WHERE chat_id = $1", chat_id)
        if not result_id:
            result_id = await connection.fetchval("INSERT INTO lists DEFAULT VALUES RETURNING id")
            await connection.execute("INSERT INTO chats (chat_id, list_id) VALUES ($1, $2)", chat_id, result_id)
        return result_id

async def add_items(pool: asyncpg.pool.Pool, list_id: int, items: list[Item]) -> dict[str, bool]:
    query_results = {}
    async with pool.acquire() as connection:
        for item in items:
            query = "INSERT INTO items(list_id, item_name, category) VALUES ($1, $2, $3) ON CONFLICT (list_id, item_name) DO NOTHING RETURNING item_name"
            result = await connection.fetchval(query, list_id, item.name, item.category)
            query_results[item.name] = (result is not None)
    return query_results

async def remove_items_by_name(pool: asyncpg.pool.Pool, list_id: int, item_names: list[str]) -> dict[str, bool]:
    query_results = {}
    async with pool.acquire() as connection:
        for item_name in item_names:
            query = "DELETE FROM items WHERE list_id = $1 AND item_name = $2 RETURNING item_name"
            result = await connection.fetchval(query, list_id, item_name)
            query_results[item_name] = (result is not None)
    return query_results

async def clear_list(pool: asyncpg.pool.Pool, list_id: int) -> int:
    query = "DELETE FROM items WHERE list_id = $1 RETURNING item_name"
    async with pool.acquire() as connection:
        deletion_records = await connection.fetch(query, list_id)
    return len(deletion_records)

async def categorize_item_by_name(pool: asyncpg.pool.Pool, list_id: int, item_name: str, category: str) -> bool:
    query = "UPDATE items SET category = $3 WHERE list_id = $1 AND item_name = $2 RETURNING item_name"
    async with pool.acquire() as connection:
        num_rows_updated = await connection.fetchval(query, list_id, item_name, category)
    return num_rows_updated >= 1


async def get_items(pool: asyncpg.pool.Pool, list_id: int) -> list[Item]:
    async with pool.acquire() as connection:
        result_records = await connection.fetch("SELECT item_name, category FROM items WHERE list_id = $1", list_id)
    return [Item(row["item_name"], row["category"]) for row in result_records]

async def get_pending_conversation(pool: asyncpg.pool.Pool, chat_id: int) -> list[dict] | None:
    async with pool.acquire() as connection:
        saved_conversation = await connection.fetchval("SELECT pending_conversation FROM chats WHERE chat_id = $1", chat_id)
        if not saved_conversation:
            return None
        return json.loads(saved_conversation)

async def save_pending_conversation(pool: asyncpg.pool.Pool, chat_id: int, contents: list[dict] | None) -> None:
    async with pool.acquire() as connection:
        contents_str = None if contents is None else json.dumps(contents)
        await connection.execute("UPDATE chats SET pending_conversation = $1 WHERE chat_id = $2", contents_str, chat_id)

async def clear_pending_conversation(pool: asyncpg.pool.Pool, chat_id: int) -> None:
    await save_pending_conversation(pool, chat_id, None)