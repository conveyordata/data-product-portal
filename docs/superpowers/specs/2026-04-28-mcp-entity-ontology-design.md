# MCP Entity Ontology Design

**Date:** 2026-04-28
**Status:** Approved
**Branch:** feature/metadata-webinar

## Overview

Add a text-based mini ontology to the MCP server so AI agents can correctly reason about entity relationships and tool-chaining without trial and error. The ontology is proactive — no specific agent failure prompted it, but the entity model (especially Input Ports as access links) is subtle enough to cause silent mistakes.

## Target

AI agents (Claude, Cursor, etc.) connecting to the MCP server. Not for human developers — those can read the code and tool docstrings.

## Architecture

Two changes, both in `backend/app/mcp/mcp.py`. No new files, no schema changes, no migrations.

### 1. Expand `FastMCP(instructions=...)` block

Append an entity hierarchy paragraph to the existing `instructions` string. The current 5-step discovery flow is preserved unchanged. The addition names the five entities, their one-line relationships, and points agents to the full ontology resource.

**Addition (appended after the existing instructions text):**

```
Entity hierarchy:
- Domain → Data Product → Output Port (primary data-sharing unit) / Technical Asset
- Input Port: the access link between a consuming Data Product and an Output Port;
  has status PENDING | APPROVED | DENIED and a justification.
- Output ports are always owned by exactly one data product; technical assets likewise.

For the full entity model, ID provenance, and relationship graph, read resource portal://ontology.
```

### 2. New `@mcp.resource("portal://ontology")`

A static function returning a plain-text structured document. No DB call, no auth required. Placed in the existing `RESOURCE ENDPOINTS` section of `mcp.py`, alongside `marketplace://overview`.

## Ontology Resource Content

```
## Entity Model

### Domain
- Contains: Data Products
- ID from: get_marketplace_overview() → domains[].id
- Resolved by: get_domain_details(domain_id)

### Data Product
- Belongs to: one Domain
- Exposes: Output Ports, Technical Assets
- Consumes via Input Ports: Output Ports from other Data Products
- ID from: search_data_products(), search_output_ports() → data_product_id,
           get_lineage_graph() → nodes where type=dataProductNode
- Resolved by: get_data_product_details(id), get_data_product_analytics(id)

### Output Port
- Belongs to: one Data Product
- Consumed by: Data Products (via Input Ports, with PENDING/APPROVED/DENIED status)
- Has: table schemas, semantic models, PII tags, freshness
- ID from: search_output_ports(), get_data_product_analytics() → analytics.output_ports[].id,
           get_lineage_graph() → nodes where type=datasetNode
- Resolved by: get_output_port_details(id), get_output_port_model(id)

### Technical Asset
- Belongs to: one Data Product
- ID from: get_data_product_analytics() → analytics.technical_assets[].id
- Resolved by: get_technical_asset_details(id)

### Input Port (access link, not directly addressable by ID)
- Connects: consuming Data Product → Output Port it requests access to
- Status: PENDING | APPROVED | DENIED
- Has: justification, requestor/approver emails, timestamps
- Found in: get_output_port_details() → consuming_data_products[]
            get_data_product_analytics() → analytics.input_ports[]

## Relationships
Domain -[contains]-> Data Product
Data Product -[exposes]-> Output Port
Data Product -[exposes]-> Technical Asset
Data Product -[consumes via Input Port]-> Output Port
Output Port -[has access grants as]-> Input Port

## Access Flow
To check if Data Product A can use Output Port B:
  get_output_port_details(B) → consuming_data_products[] → filter by consuming_data_product_id == A → check status
```

## What is NOT included

- Tool routing matrix (duplicates tool docstrings, goes stale)
- Prose-only definitions (too loose for agent reasoning)
- Separate file or external doc (everything stays in `mcp.py`)

## Implementation Steps

1. In `FastMCP(instructions=...)`, append the entity hierarchy paragraph
2. Add `@mcp.resource("portal://ontology")` static function returning the ontology text
3. Verify both are present and correctly formatted
