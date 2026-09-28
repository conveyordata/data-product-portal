import asyncio

from fastmcp import FastMCP

from portal_plugins.glue.mcp_instructions import MCP_INSTRUCTIONS
from portal_plugins.glue.schema import GlueTechnicalAssetConfiguration


def test_mcp_instructions__matches_the_plugins_own_instructions():
    assert GlueTechnicalAssetConfiguration.mcp_instructions == MCP_INSTRUCTIONS


def test_register_mcp_tools__registers_every_glue_tool():
    mcp = FastMCP()

    GlueTechnicalAssetConfiguration.register_mcp_tools(mcp)

    tools = {tool.name for tool in asyncio.run(mcp.list_tools())}
    assert tools == {
        "get_aws_credentials",
        "get_glue_database",
        "list_glue_tables",
        "query_athena",
        "get_athena_query_results",
    }
