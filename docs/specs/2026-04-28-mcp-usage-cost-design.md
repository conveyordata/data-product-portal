# MCP Usage & Cost Tool Design

**Date:** 2026-04-28
**Branch:** feature/metadata-webinar
**Scope:** `backend/app/mcp/mcp.py` only — no frontend, CLI, or API route changes

## Goal

Enable an AI agent to answer: *"What did Marketing Customer 360 cost last month, and which consumers drove the most queries?"*

## New Tool: `get_data_product_usage`

### Signature

```python
@mcp.tool
def get_data_product_usage(data_product_id: str, day_range: int = 30) -> Dict[str, Any]:
```

**Parameters:**
- `data_product_id`: UUID string, obtained from `search_data_products` or `get_data_product_details`
- `day_range`: Number of days to look back (default 30, configurable)

### Placement

Added to the `DETAILED ENTITY INFORMATION` section of `mcp.py`, alongside `get_data_product_details` and `get_data_product_analytics`.

### Service Calls

1. **Cost:** `OutputPortCostService(db).get_data_product_cost_summary(UUID(data_product_id), day_range)`
   Already exists. Returns cost broken down by output port across the date range.

2. **Query stats:** For each output port retrieved via `OutputPortService(db).get_output_ports(user, UUID(data_product_id))`, call `OutputPortStatsService(db).get_query_stats(dataset_id, granularity=QueryStatsGranularity.DAY, day_range=day_range)`.
   Aggregate `query_count` per `consumer_data_product_id` across all days, sort descending to produce a ranked top-consumers list per output port.

No new services or models required.

### Response Shape

```json
{
  "data_product_id": "<uuid>",
  "day_range": 30,
  "cost_summary": {
    "total_cost": 1234.56,
    "by_output_port": [
      {
        "output_port_id": "<uuid>",
        "output_port_name": "Customer Segments",
        "compute_cost": 800.00,
        "storage_cost": 200.00,
        "platform_overhead_cost": 50.00,
        "total_cost": 1050.00
      }
    ]
  },
  "consumer_query_stats": [
    {
      "output_port_id": "<uuid>",
      "output_port_name": "Customer Segments",
      "top_consumers": [
        {
          "consumer_data_product_id": "<uuid>",
          "consumer_data_product_name": "Marketing Analytics",
          "total_queries": 4200
        }
      ]
    }
  ]
}
```

### Error Handling

Consistent with existing MCP tools:
- Data product not found → `{"error": "Data product {id} not found"}`
- No cost records in range → `cost_summary.by_output_port: []`, `total_cost: 0`
- No query stats in range → `consumer_query_stats` entries have `top_consumers: []`
- Any exception → `{"error": "Failed to get data product usage: {str(e)}"}`

### Auth

Requires `get_access_token()` — same pattern as `get_data_product_analytics` — because `OutputPortService.get_output_ports()` requires a `User` object. Call `get_mcp_authenticated_user(token=access_token.token)` to resolve the user from the token before fetching output ports.

## Imports to Add

```python
from app.data_products.output_ports.cost.service import OutputPortCostService
from app.data_products.output_ports.query_stats.service import (
    OutputPortStatsService,
    QueryStatsGranularity,
)
```

## MCP Instructions Update

Add `get_data_product_usage` to the recommended discovery flow in the `mcp` server instructions, after `get_data_product_analytics`:

> 4. get_data_product_usage: get cost breakdown and top consumer query stats for a data product over a time window
