# Design: `get_output_port_model` MCP Tool

**Date:** 2026-04-28
**Scope:** MCP server only (`backend/app/mcp/mcp.py`)

## Goal

Enable AI agents to answer compliance and PII questions such as:
- "Are any output ports of the Marketing Customer 360 data product at risk of compliance issues?"
- "What kind of PII data is exposed by the Marketing Customer 360 data product?"

The agent pairs this tool with `get_data_product_details` (for the data product's `about` field — the legal/compliance context) and reasons over the combined data.

## New Tool: `get_output_port_model`

Single new `@mcp.tool` function added to `backend/app/mcp/mcp.py`.

### Signature

```python
def get_output_port_model(output_port_id: str) -> Dict[str, Any]
```

### Response Structure

```json
{
  "output_port": {
    "id": "<uuid>",
    "name": "...",
    "description": "...",
    "about": "...",
    "access_type": "...",
    "tags": [{"id": "...", "value": "..."}]
  },
  "table_schemas": [
    {
      "id": "<uuid>",
      "name": "...",
      "description": "...",
      "tags": [{"id": "...", "value": "..."}],
      "columns": [
        {
          "id": "<uuid>",
          "name": "...",
          "description": "...",
          "data_type": "...",
          "tags": [{"id": "...", "value": "PII"}]
        }
      ]
    }
  ],
  "semantic_models": [
    {
      "id": "<uuid>",
      "output_port_id": "<uuid>",
      "name": "...",
      "format": "MetricsFlow",
      "content": { }
    }
  ]
}
```

### Implementation

Three service calls, all within a single DB session:

1. `OutputPortService(db).get_dataset(id=UUID(output_port_id), user=user)` — output port metadata
2. `TableSchemaService(db).get_all(UUID(output_port_id))` — table schemas with columns and tags (eagerly loaded)
3. `SemanticModelService(db).get_all(UUID(output_port_id))` — semantic model definitions

Serialized via existing Pydantic models:
- `TableSchemaResponse` + `ColumnResponse` (from `table_schemas/schema_response.py`)
- `SemanticModelResponse` (from `semantic_models/schema_response.py`)
- Output port fields selected manually (name, description, about, access_type, tags)

### Tool Docstring Guidance

The docstring should instruct the AI:
- Use this to inspect the data model and semantic metadata of a single output port
- Column-level `tags` contain PII and sensitivity classifications
- Table-level `tags` contain dataset-level classifications
- `semantic_models` contain business entity definitions (entities, metrics, dimensions)
- For compliance questions, combine with `get_data_product_details` to get the data product's `about` (legal/compliance context)

## Discovery Flow for Compliance Questions

```
search_data_products("Marketing Customer 360")
  → get_data_product_details(data_product_id)       # legal/compliance context via `about`
  → get_data_product_analytics(data_product_id)     # list of output ports
  → get_output_port_model(output_port_id)            # schema + PII tags + semantic model
    (repeat for each output port)
```

## Required Imports

Add to `mcp.py`:
```python
from app.data_products.output_ports.table_schemas.service import TableSchemaService
from app.data_products.output_ports.table_schemas.schema_response import TableSchemaResponse
from app.data_products.output_ports.semantic_models.service import SemanticModelService
from app.data_products.output_ports.semantic_models.schema_response import SemanticModelResponse
```

## Constraints

- MCP server only — no changes to routers, services, models, or schemas outside `mcp.py`
- No new Pydantic models needed; existing response schemas cover all fields
- Authentication: uses `get_access_token()` + `get_mcp_authenticated_user()` (same pattern as `get_output_port_details`)
