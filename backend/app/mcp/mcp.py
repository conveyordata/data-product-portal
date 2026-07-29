"""Data Product Portal MCP server.

Structure:
  mcp.py               — this file: server initialization and plugin loader
  deps.py              — shared infrastructure (DB session, auth)
  loader.py            — discovers and registers tools from all AssetProviderPlugin subclasses

  search.py            — discovery and search tools
  details.py           — detail retrieval tools for entities
  config.py            — marketplace overview, environments, analytics
  resources.py         — resource endpoints
  permissions.py       — role assignments and user permissions

  data_output_configuration/<name>/mcp_tools.py
                       — per-plugin tool registrations (e.g. Glue/Athena)
"""

from typing import get_args

from fastmcp import FastMCP

from app.core.logging import logger
from app.mcp.config import register_config_tools
from app.mcp.deps import get_auth_provider, initialize_models
from app.mcp.details import register_detail_tools
from app.mcp.loader import get_plugin_instructions, load_plugins
from app.mcp.permissions import register_permission_tools
from app.mcp.resources import register_resources
from app.mcp.search import register_search_tools
from app.technical_asset_configuration.schema_union import DataOutputs

initialize_models()

_BASE_INSTRUCTIONS = """
Portal for discovering and exploring data products and output ports.

CORE CONCEPTS:
- Output ports (datasets) = published, queryable datasets
- Data products = containers grouping related output ports and infrastructure
- Technical assets = underlying infrastructure (e.g. Glue databases)
- Environments = deployment stages (prod, staging, dev)

═══════════════════════════════════════════════════════════════════════
TWO DISTINCT MODES OF OPERATION
═══════════════════════════════════════════════════════════════════════

MODE 1: DISCOVERY (Metadata Only — Fast, No Credentials Required)
──────────────────────────────────────────────────────────────────────
Tools for Discovery (no credentials needed):
- search_output_ports(query)      — find datasets
- search_data_products(query)     — find data products
- get_output_port_details(id)     — metadata about a dataset
- get_data_product_details(id)    — details about a data product
- get_data_product_analytics(id)  — what output ports a data product has
- get_marketplace_overview()      — high-level statistics
- get_environments()              — available environments

MODE 2: DATA QUERIES (Actual Data — Requires Credentials)
──────────────────────────────────────────────────────────────────────
DATA QUERY FLOW — Steps 1–3 (common to all plugins)

Step 1: DISCOVER THE DATA
  search_output_ports("user's query")

Step 2: GET METADATA & CONSUMING DATA PRODUCTS 🔑
  get_output_port_details(output_port_id)
  → data_product_links contains consuming data products — these are typically
    your access path to query the data
  → Also use get_consuming_products(output_port_id, data_product_id)

Step 3: DETERMINE ENVIRONMENT
  Call get_environments() if the user didn't specify one.

Steps 4+ are provided by the active data-access plugin (e.g. Glue/Athena).

═══════════════════════════════════════════════════════════════════════
GENERAL RULES
═══════════════════════════════════════════════════════════════════════
✓ Route to Discovery mode for metadata questions (no credentials needed)
✓ ALWAYS extract data_product_links from output port details
✓ TRY CONSUMING DATA PRODUCTS FIRST — most common access pattern
✗ Don't request credentials for pure metadata questions
"""

mcp = FastMCP(
    name="DataProductPortalMCP",
    instructions=_BASE_INSTRUCTIONS + get_plugin_instructions(),
    auth=get_auth_provider(),
)

register_search_tools(mcp)
register_detail_tools(mcp)
register_config_tools(mcp)
register_resources(mcp)
register_permission_tools(mcp)

load_plugins(mcp)

logger.info(
    "[MCP] Server ready. Active plugins: "
    + str([cls.__name__ for cls in get_args(DataOutputs) if cls.mcp_instructions])
)
