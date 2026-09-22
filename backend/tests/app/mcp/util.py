import asyncio
from unittest.mock import patch

from fastmcp import Client, FastMCP
from fastmcp.client.client import CallToolResult
from fastmcp.client.tasks import ToolTask
from sqlalchemy.orm import Session

from app.users.model import User as UserModel


def call_mcp_tool(
    mcp_server: FastMCP,
    session: Session,
    user: UserModel,
    tool_name: str,
    arguments: dict[str, object] | None = None,
) -> CallToolResult | ToolTask:
    with (
        patch("app.database.database.SessionLocal", return_value=session),
        patch.object(session, "commit"),
        patch.object(session, "close"),
        patch("app.mcp.deps.get_authenticated_user", return_value=user),
    ):

        async def call():
            async with Client(mcp_server) as client:
                return await client.call_tool(tool_name, arguments or {})

        return asyncio.run(call())
