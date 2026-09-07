from mcp.server.mcpserver import MCPServer

import db
from models.item import Item
from category.categorizer import find_category
from parsing_utils import normalize_name

def build_mcp_server(pool, list_id, chat_id, contents) -> MCPServer:
    server = MCPServer(name="grocery-list")

    @server.tool()
    async def add_items_to_list(item_names: list[str]) -> dict[str, bool]:
        items = [Item(normalize_name(item_name), find_category(item_name)) for item_name in item_names]
        return await db.add_items(pool, list_id, items)

    @server.tool()
    async def remove_items_from_list(item_names: list[str]) -> dict[str, bool]:
        normalized_item_names = [normalize_name(item_name) for item_name in item_names]
        return await db.remove_items_by_name(pool, list_id, normalized_item_names)

    @server.tool()
    async def get_list() -> dict[str, str | None]:
        item_list = await db.get_items(pool, list_id)
        return {item.name: item.category for item in item_list}

    @server.tool()
    async def categorize_items(item_names: list[str], category: str) -> dict[str, bool]:
        category = normalize_name(category)
        result = {}
        for item_name in item_names:
            item_name = normalize_name(item_name)
            result |= await db.categorize_item_by_name(pool, list_id, item_name, category)
        return result

    @server.tool()
    async def query_user(question: str) -> dict[str, bool]:
        serializable_contents = [content.model_dump(mode='json') for content in contents]
        await db.save_pending_conversation(pool, chat_id, serializable_contents)
        return {"asked": True}

    return server