from __future__ import annotations

import os

from fastmcp import Client, FastMCP
from fastmcp.client.auth.oauth import OAuth
from fastmcp.utilities.logging import get_logger
from key_value.aio.stores.memory import MemoryStore

logger = get_logger(__name__)

endpoint = os.getenv("ENDPOINT", "http://localhost:5050")
oauth = OAuth(
    mcp_url=f"{endpoint}/mcp/mcp", callback_port=57453, token_storage=MemoryStore()
)
client = Client(f"{endpoint}/mcp/mcp", auth=oauth)

server = FastMCP.as_proxy(client, name="AuthenticatedProxyDataProductPortal")

if __name__ == "__main__":
    server.run()
