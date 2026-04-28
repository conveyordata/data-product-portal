# MCP Entity Ontology Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a structured entity ontology to the MCP server so AI agents can correctly reason about entity relationships, UUID provenance, and tool-chaining.

**Architecture:** Expand the existing `FastMCP(instructions=...)` block with a short entity hierarchy summary and a pointer to a new `@mcp.resource("portal://ontology")` static function. No DB calls, no auth, no new files — two edits to one file.

**Tech Stack:** Python, FastMCP (`backend/app/mcp/mcp.py`)

---

## File Structure

| Action | Path | Change |
|--------|------|--------|
| Modify | `backend/app/mcp/mcp.py` | Add entity hierarchy to `instructions` block; add `portal://ontology` resource |
| Create | `backend/tests/app/mcp/test_ontology_resource.py` | Unit tests for the new resource function |

---

## Task 1: Write failing tests for the ontology resource

**Files:**
- Create: `backend/tests/app/mcp/test_ontology_resource.py`

- [ ] **Step 1: Create the test file**

```python
# ruff: noqa: S106
from app.mcp.mcp import get_ontology_resource  # type: ignore[attr-defined]


class TestOntologyResource:
    def test_contains_entity_model_section(self):
        content = get_ontology_resource()
        assert "## Entity Model" in content

    def test_contains_all_five_entities(self):
        content = get_ontology_resource()
        assert "### Domain" in content
        assert "### Data Product" in content
        assert "### Output Port" in content
        assert "### Technical Asset" in content
        assert "### Input Port" in content

    def test_contains_relationships_section(self):
        content = get_ontology_resource()
        assert "## Relationships" in content
        assert "-[contains]->" in content
        assert "-[exposes]->" in content
        assert "-[consumes via Input Port]->" in content

    def test_contains_access_flow_section(self):
        content = get_ontology_resource()
        assert "## Access Flow" in content
        assert "PENDING" in content
        assert "APPROVED" in content
        assert "DENIED" in content

    def test_contains_id_provenance_for_each_entity(self):
        content = get_ontology_resource()
        assert "get_marketplace_overview()" in content
        assert "search_data_products()" in content
        assert "search_output_ports()" in content
        assert "get_data_product_analytics()" in content

    def test_contains_resolved_by_for_each_entity(self):
        content = get_ontology_resource()
        assert "get_domain_details" in content
        assert "get_data_product_details" in content
        assert "get_output_port_details" in content
        assert "get_output_port_model" in content
        assert "get_technical_asset_details" in content
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd backend && poetry run pytest tests/app/mcp/test_ontology_resource.py -v
```

Expected: `ImportError` or `AttributeError` — `get_ontology_resource` does not exist yet.

---

## Task 2: Implement the ontology resource

**Files:**
- Modify: `backend/app/mcp/mcp.py` (RESOURCE ENDPOINTS section, after `get_marketplace_resource`)

- [ ] **Step 1: Add the ontology resource function**

In `backend/app/mcp/mcp.py`, locate the `RESOURCE ENDPOINTS` section (around line 919). After the `get_marketplace_resource` function, add:

```python
@mcp.resource("portal://ontology")
def get_ontology_resource() -> str:
    """Entity model and relationship graph for the Data Product Portal.
    Read this when you need to understand how entities relate, where UUIDs come from,
    or which tool to call to resolve a given entity type."""
    return """
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
"""
```

- [ ] **Step 2: Run tests to confirm they pass**

```bash
cd backend && poetry run pytest tests/app/mcp/test_ontology_resource.py -v
```

Expected: All 6 tests PASS.

---

## Task 3: Update the FastMCP instructions block

**Files:**
- Modify: `backend/app/mcp/mcp.py` lines 90–109 (the `FastMCP(...)` constructor call)

- [ ] **Step 1: Append entity hierarchy to the instructions string**

Replace the existing `instructions=` value (which ends with `"Data products are containers owned by teams that group related output ports and technical assets."`) with:

```python
mcp = FastMCP(
    name="DataProductPortalMCP",
    instructions="""
    Portal for discovering and exploring data products and output ports.

    Recommended discovery flow:
    1. get_marketplace_overview: understand what's available and get domain IDs
    2. search_output_ports: find specific output ports (preferred for most searches)
       Use search_data_products only when the user explicitly asks to find a data product.
    3. get_*_details: drill into a specific result by UUID
    4. get_data_product_usage: get cost breakdown and top consumer query stats for a data product
    5. get_lineage_graph: traverse the full data lineage graph to answer connection-based
       questions (deprecation impact, upstream/downstream dependencies, transitive consumers).
       Edges with animated=true are APPROVED access links; animated=false are pending.

    Output ports (datasets) are the primary way data is shared in the portal.
    Data products are containers owned by teams that group related output ports and technical assets.

    Entity hierarchy:
    - Domain → Data Product → Output Port (primary data-sharing unit) / Technical Asset
    - Input Port: the access link between a consuming Data Product and an Output Port;
      has status PENDING | APPROVED | DENIED and a justification.
    - Output ports are always owned by exactly one data product; technical assets likewise.

    For the full entity model, ID provenance, and relationship graph, read resource portal://ontology.
    """,
    auth=get_auth_provider(),
)
```

- [ ] **Step 2: Run the full MCP test suite to confirm no regressions**

```bash
cd backend && poetry run pytest tests/app/mcp/ -v
```

Expected: All tests PASS including the 6 new ones in `test_ontology_resource.py`.

- [ ] **Step 3: Commit**

```bash
git add backend/app/mcp/mcp.py backend/tests/app/mcp/test_ontology_resource.py
git commit -m "feat(mcp): add portal://ontology resource and entity hierarchy to instructions"
```
