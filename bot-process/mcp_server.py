from mcp.server.mcpserver import MCPServer
from db import add_items, remove_items_by_name, get_items, save_pending_conversation
from models.item import Item

def build_mcp_server(pool, list_id, chat_id, contents) -> MCPServer:
    server = MCPServer(name="grocery-list")

    @server.tool()
    async def add_items_to_list(item_names: list[str]) -> dict[str, bool]:
        # TODO: Use item categorization once implemented
        items = [Item(item_name, None) for item_name in item_names]
        return await add_items(pool, list_id, items)

    @server.tool()
    async def remove_items_from_list(item_names: list[str]) -> dict[str, bool]:
        return await remove_items_by_name(pool, list_id, item_names)

    @server.tool()
    async def get_list() -> dict[str, str | None]:
        item_list = await get_items(pool, list_id)
        return {item.name: item.category for item in item_list}

    @server.tool()
    async def query_user(question: str) -> dict[str, bool]:
        serializable_contents = [content.model_dump(mode='json') for content in contents]
        await save_pending_conversation(pool, chat_id, serializable_contents)
        return {"asked": True}

    return server