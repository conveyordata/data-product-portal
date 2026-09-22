import asyncio
from unittest.mock import patch

from fastmcp import Client

from app.settings import settings


def call_mcp_tool(
    mcp_server,
    session,
    user,
    tool_name: str,
    arguments: dict | None = None,
):
    with (
        patch("app.database.database.SessionLocal", return_value=session),
        patch.object(session, "commit"),
        patch.object(session, "close"),
        patch.object(settings, "DEFAULT_USERNAME", user.external_id),
    ):

        async def call():
            async with Client(mcp_server) as client:
                return await client.call_tool(tool_name, arguments or {})

        return asyncio.run(call())
