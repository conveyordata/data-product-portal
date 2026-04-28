# MCP Freshness Enrichment — Design Spec

**Date:** 2026-04-28
**Status:** Approved

## Problem

When an agent is asked "Marketing Customer 360 looks stale this morning — which upstream is the problem and who do I contact?", it can use the MCP to find the data product, list its input ports (upstream output ports), and retrieve owner contact info. However, it cannot identify *which* upstream is stale because freshness data is not exposed through the MCP.

Freshness is fully modelled in the backend (`FreshnessSlo`, `FreshnessObservation`, `FreshnessService`) but not surfaced in any MCP tool or resource.

## Scope

One change to one file: `backend/app/mcp/mcp.py`.

No changes to REST API schemas, Pydantic response models, or service layer.

## Design

### Tool: `get_output_port_details`

After the existing dataset fetch, call `FreshnessService` in the same DB session and merge a `freshness` block into the returned dict.

**Added queries (in order):**
1. `FreshnessService(db).get_slo(output_port_id)` — wrapped in try/except for `HTTPException(404)` (no SLO = not configured).
2. `FreshnessService(db).get_latest_observation(output_port_id)` — returns `None` if no observations recorded yet.
3. `FreshnessService(db).compute_status(dataset)` — derives `FRESH` / `STALE` / `UNKNOWN` from the already-loaded `dataset` ORM object; no additional DB query.

**Response shape (always present, consistent):**

```json
"freshness": {
  "status": "stale",
  "slo_deadline": "08:00:00",
  "last_refreshed_at": "2026-04-27T07:45:00Z",
  "last_observed_at": "2026-04-27T07:45:01Z"
}
```

| Field | Type | Null when |
|---|---|---|
| `status` | `"fresh"` \| `"stale"` \| `"unknown"` | Never — always present |
| `slo_deadline` | `time` string | No SLO configured |
| `last_refreshed_at` | ISO datetime string | No observations recorded |
| `last_observed_at` | ISO datetime string | No observations recorded |

When no SLO is configured, `status` is `"unknown"` and both timestamp fields are `null`.

### Imports to add

```python
from app.data_products.output_ports.freshness.service import FreshnessService
from app.data_products.output_ports.freshness.schema_response import FreshnessSloResponse
```

`FreshnessStatus` does not need to be imported directly — the service returns enum values that serialise as strings.

## Error handling

- Missing SLO: caught with `except HTTPException` → all freshness fields default to `null` / `"unknown"`.
- Any other exception in the freshness block: does not suppress the main response; logged and freshness block returned with `"unknown"` status and nulls.

## Testing

- Unit test: output port with SLO + observations → `status` is `"fresh"` or `"stale"`.
- Unit test: output port with SLO, no observations → `status` is `"unknown"`, timestamps null.
- Unit test: output port with no SLO → `status` is `"unknown"`, all fields null.

## Out of scope

- Freshness in `search_output_ports` results.
- Freshness in the `output-port://` resource.
- Any changes to REST API schemas or service layer.
