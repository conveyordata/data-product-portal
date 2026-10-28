"""Tests for the `get_user_roles` MCP tool.

Also serves as the reference pattern for testing FastMCP tools: call them
through `fastmcp.Client(mcp)` so the request goes through the real DI/protocol
stack (dependency resolution, context managers, etc.), instead of invoking the
underlying function directly and bypassing that machinery.
"""

import asyncio

from fastmcp import Client

from app.mcp.mcp import mcp
from tests.factories import GlobalRoleAssignmentFactory, RoleFactory, UserFactory
from tests.session_util import as_user


def call_mcp_tool(tool_name: str, arguments: dict):
    """Call an MCP tool through the real FastMCP client/DI stack."""

    async def call():
        async with Client(mcp) as client:
            return await client.call_tool(tool_name, arguments)

    return asyncio.run(call())


def test_get_user_roles__end_to_end_through_mcp_protocol(session):
    """Regression test for `get_user_db_session`.

    Calls the `get_user_roles` tool through the real FastMCP dependency
    injection/protocol stack (not by invoking the underlying function
    directly). Before the fix, `get_user_db_session` was a plain generator
    passed as a `Depends` factory without `@contextmanager`, so the DI engine
    resolved `db` to the raw generator object instead of entering it,
    and any `db.scalars(...)` call raised
    `AttributeError: 'generator' object has no attribute 'scalars'`.
    """
    user = UserFactory()
    role = RoleFactory(scope="global")
    GlobalRoleAssignmentFactory(identity_id=user.id, role_id=role.id)

    with as_user(session, user.id):
        result = call_mcp_tool("get_user_roles", {"user_id": str(user.id)})

    data = result.data
    assert data["user_id"] == str(user.id)
    assert data["summary"]["global_roles_count"] == 1
