import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastmcp import Client, FastMCP
from fastmcp.dependencies import Depends

from app.mcp.deps import get_mcp_authenticated_user
from app.mcp.middleware import LoggingMiddleware


def build_server(posthog):
    with patch(
        "app.core.logging.posthog_analytics.get_posthog_client",
        return_value=posthog,
    ):
        middleware = LoggingMiddleware()
    server = FastMCP("test")
    server.add_middleware(middleware)

    @server.tool
    def whoami(user=Depends(get_mcp_authenticated_user)) -> str:
        return str(user.id)

    return server


def captured(posthog, method):
    return [
        call.kwargs
        for call in posthog.capture.call_args_list
        if call.kwargs["properties"]["method"] == method
    ]


class TestLoggingMiddleware:
    def test_on_message__captures_user_resolved_by_tool(self):
        posthog = MagicMock()
        server = build_server(posthog)
        user_id = uuid4()

        async def run():
            async with Client(server) as client:
                await client.list_tools()
                await client.call_tool("whoami", {})

        with patch(
            "app.mcp.deps._resolve_mcp_user",
            return_value=SimpleNamespace(id=user_id),
        ):
            asyncio.run(run())

        [tool_call] = captured(posthog, "tools/call")
        assert tool_call["distinct_id"] == str(user_id)
        assert tool_call["event"] == "MCP Method Call API"
        assert (
            tool_call["timestamp"].isoformat() == tool_call["properties"]["timestamp"]
        )
        assert '"whoami"' in tool_call["properties"]["payload"]
        [list_call] = captured(posthog, "tools/list")
        assert list_call["distinct_id"] == "unknown"

    def test_on_message__user_lookup_failure_keeps_tool_result(self):
        posthog = MagicMock()
        server = build_server(posthog)

        async def run():
            async with Client(server) as client:
                return await client.call_tool("whoami", {})

        with (
            patch(
                "app.mcp.deps._resolve_mcp_user",
                return_value=SimpleNamespace(id=uuid4()),
            ),
            patch(
                "fastmcp.server.context.Context.get_state",
                side_effect=RuntimeError("state store down"),
            ),
        ):
            result = asyncio.run(run())

        assert not result.is_error
        [tool_call] = captured(posthog, "tools/call")
        assert tool_call["distinct_id"] == "unknown"
