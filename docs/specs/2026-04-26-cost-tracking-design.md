# Cost Tracking — Design Spec

**Date:** 2026-04-26
**Status:** Approved

---

## Overview

Cost tracking allows teams to attribute infrastructure costs to their output ports and view them aggregated at the data product level. Cost data is pushed programmatically by external billing systems via API. The v1 scope covers cost recording and display on the data product page only; output port page display and upstream cost exposure are deferred to v2.

---

## Scope (v1)

**In scope:**
- API to push cost records per output port (compute, storage, platform overhead)
- API to retrieve cost history per output port
- API to retrieve total cost summary for a data product (latest record per output port, broken down)
- New "Costs" tab on the data product page

**Deferred to v2:**
- Output port page cost display (direct cost widget, upstream exposure widget)
- Upstream cost exposure API endpoint
- Cost trend charts

---

## Data Model

### New table: `output_port_cost_records`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | Primary key |
| `output_port_id` | UUID | FK → `datasets.id`, CASCADE delete |
| `recorded_at` | DateTime | `server_default=utcnow()`, indexed |
| `compute_cost` | Numeric(12,4) | EUR, required |
| `storage_cost` | Numeric(12,4) | EUR, required |
| `platform_overhead_cost` | Numeric(12,4) | EUR, required |

- `total_cost` is a computed property (`compute_cost + storage_cost + platform_overhead_cost`), not stored.
- All three cost columns are non-nullable. Zero is a valid value.
- Currency is fixed to EUR for v1.
- All records are retained (historical series).

### Relationship added to `Dataset` model

```python
cost_records: Mapped[list["OutputPortCostRecord"]] = relationship(
    cascade="all, delete-orphan",
    order_by="OutputPortCostRecord.recorded_at.desc()",
    lazy="raise",
)
```

The latest record is fetched in the service layer, not as a joined relationship, to avoid loading full history on every output port load.

---

## Backend

### Module structure

Follows the existing `output_ports/data_quality/` pattern exactly:

```
backend/app/data_products/output_ports/cost/
    __init__.py
    model.py
    schema_request.py
    schema_response.py
    service.py
    router.py
```

### API endpoints

#### Output port cost

Base route: `/v2/data_products/{data_product_id}/output_ports/{id}/cost`

**`POST /cost`** — Push a cost record
Auth: new `OUTPUT_PORT__UPDATE_COST` Casbin action (parallel to `OUTPUT_PORT__UPDATE_DATA_QUALITY`)

Request body:
```json
{
  "compute_cost": 45.00,
  "storage_cost": 30.00,
  "platform_overhead_cost": 15.00
}
```

Response `201`:
```json
{
  "id": "...",
  "output_port_id": "...",
  "recorded_at": "2026-04-01T00:00:00Z",
  "compute_cost": 45.00,
  "storage_cost": 30.00,
  "platform_overhead_cost": 15.00,
  "total_cost": 90.00
}
```

**`GET /cost`** — Fetch cost history
Auth: no special auth (same as other GET endpoints on output ports)
Query params: `limit` (default 90)

Response:
```json
{
  "output_port_id": "...",
  "records": [
    {
      "id": "...",
      "recorded_at": "2026-04-01T00:00:00Z",
      "compute_cost": 45.00,
      "storage_cost": 30.00,
      "platform_overhead_cost": 15.00,
      "total_cost": 90.00
    }
  ]
}
```

#### Data product cost summary

Implemented in `backend/app/data_products/router.py` (added directly, not a sub-module — only one endpoint).

Route: `GET /v2/data_products/{id}/cost`

Aggregates the latest cost record from each output port belonging to this data product. Output ports with no cost data are excluded.

Response:
```json
{
  "data_product_id": "...",
  "total_cost": 240.00,
  "breakdown": [
    {
      "output_port_id": "...",
      "output_port_name": "sales_orders",
      "compute_cost": 80.00,
      "storage_cost": 40.00,
      "platform_overhead_cost": 30.00,
      "total_cost": 150.00
    }
  ]
}
```

### Authorization

A new `OUTPUT_PORT__UPDATE_COST` action is added to the Casbin RBAC model, following the same pattern as `OUTPUT_PORT__UPDATE_DATA_QUALITY`. The router registers this action as a dependency on the POST endpoint.

### Alembic migration

A single migration creates the `output_port_cost_records` table with a FK constraint and a `recorded_at` index.

---

## Frontend

### New tab: Costs

Added to `data-product-tabs/` with tab key `"costs"` inserted between `"usage"` and `"inputs"` in `TabKeys` enum.

New components:
- `CostsTab` — tab root in `data-product-tabs/costs-tab/costs-tab.tsx`
- `DataProductCostSummary` — total cost card showing the grand total in EUR
- `OutputPortCostTable` — breakdown table with columns: Output Port, Compute, Storage, Platform Overhead, Total, Share (proportional bar). Includes a totals footer row.

### Costs tab layout

```
┌─────────────────────────────────────────┐
│  Total Monthly Cost                     │
│  €240.00                                │
│  Based on latest cost record per port   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Cost by Output Port                                         │
├──────────────────┬─────────┬─────────┬──────────┬───────┬──┤
│ Output Port      │ Compute │ Storage │ Platform │ Total │  │
├──────────────────┼─────────┼─────────┼──────────┼───────┼──┤
│ sales_orders     │ €80.00  │ €40.00  │ €30.00   │€150   │▓▓│
│ customer_profiles│ €50.00  │ €20.00  │ €20.00   │ €90   │▓ │
├──────────────────┼─────────┼─────────┼──────────┼───────┼──┤
│ Total            │€130.00  │ €60.00  │ €50.00   │€240   │  │
└──────────────────┴─────────┴─────────┴──────────┴───────┴──┘
```

Output ports with no cost data are excluded from the table and total.

### RTK Query

After the backend is implemented, run `npm run generate-api` to regenerate the API client. No manual API client code.

---

## Out of scope (v2 and beyond)

- **Output port page**: Direct cost widget and upstream cost exposure widget in the sidebar
- **Upstream cost exposure API**: `GET /cost/upstream` endpoint computing proportional upstream share
- **Cost trend charts**: Time-series visualisation on the Costs tab
- **Multi-currency support**: Currently hardcoded to EUR
- **Configurable cost categories**: Currently fixed to compute, storage, platform overhead
