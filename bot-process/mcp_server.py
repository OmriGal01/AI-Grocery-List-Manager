from mcp.server.mcpserver import MCPServer
from db import add_items, remove_items, get_items

def build_mcp_server(pool, list_id) -> MCPServer:
    server = MCPServer(name="grocery-list")

    @server.tool()
    async def add_items_to_list(item_names: list[str]) -> dict[str, bool]:
        return await add_items(pool, list_id, item_names)

    @server.tool()
    async def remove_items_from_list(item_names: list[str]) -> dict[str, bool]:
        return await remove_items(pool, list_id, item_names)

    @server.tool()
    async def get_list() -> list[str]:
        return await get_items(pool, list_id, None)

    return server