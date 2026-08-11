from mcp.server.mcpserver import MCPServer
from db import add_items, remove_items, get_items, save_pending_conversation

def build_mcp_server(pool, list_id, chat_id, contents) -> MCPServer:
    server = MCPServer(name="grocery-list")

    @server.tool()
    async def add_items_to_list(item_names: list[str]) -> dict[str, bool]:
        return await add_items(pool, list_id, chat_id, item_names)

    @server.tool()
    async def remove_items_from_list(item_names: list[str]) -> dict[str, bool]:
        return await remove_items(pool, list_id, chat_id, item_names)

    @server.tool()
    async def get_list() -> list[str]:
        return await get_items(pool, list_id, chat_id, None)

    @server.tool()
    async def query_user(question: str) -> dict[str, bool]:
        serializable_contents = [content.model_dump(mode='json') for content in contents]
        await save_pending_conversation(pool, chat_id, serializable_contents)
        return {"asked": True}

    return server