# MCP `get_data_product_usage` Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `get_data_product_usage` MCP tool to `backend/app/mcp/mcp.py` that returns cost breakdown and per-output-port consumer query stats for a data product over a configurable time window.

**Architecture:** Single function added to the existing `DETAILED ENTITY INFORMATION` section. It composes two existing services — `OutputPortCostService` for cost and `OutputPortStatsService` for query stats — and aggregates query counts per consumer per output port. No new files, services, or models are required.

**Tech Stack:** Python 3.13, FastMCP, SQLAlchemy ORM, Pydantic v2, pytest with `unittest.mock`.

---

## File Map

| Action | File |
|--------|------|
| Modify | `backend/app/mcp/mcp.py` — add imports, new tool, update `instructions` string |
| Create | `backend/tests/app/mcp/test_get_data_product_usage.py` — unit tests for the new tool |

---

## Task 1: Write failing tests for `get_data_product_usage`

**Files:**
- Create: `backend/tests/app/mcp/test_get_data_product_usage.py`

The test pattern for MCP tools in this project (see `backend/tests/app/mcp/test_get_output_port_details_freshness.py`) is:
- Import the tool function directly from `app.mcp.mcp`
- Use `@patch` to mock all dependencies (`get_db_session`, `get_access_token`, `get_mcp_authenticated_user`, and each service class)
- Call the function directly and assert on the returned dict

- [ ] **Step 1: Create the test file**

```python
# ruff: noqa: S106
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.mcp.mcp import get_data_product_usage

DATA_PRODUCT_ID = str(uuid4())
OUTPUT_PORT_ID_A = str(uuid4())
OUTPUT_PORT_ID_B = str(uuid4())
CONSUMER_ID_1 = str(uuid4())
CONSUMER_ID_2 = str(uuid4())


def _make_cost_row(output_port_id, name, compute, storage, overhead):
    row = MagicMock()
    row.output_port_id = output_port_id
    row.output_port_name = name
    row.compute_cost = Decimal(str(compute))
    row.storage_cost = Decimal(str(storage))
    row.platform_overhead_cost = Decimal(str(overhead))
    return row


def _make_stat(date_str, consumer_id, consumer_name, query_count):
    stat = MagicMock()
    stat.consumer_data_product_id = consumer_id
    stat.consumer_data_product_name = consumer_name
    stat.query_count = query_count
    return stat


def _make_output_port(port_id, name):
    op = MagicMock()
    op.id = port_id
    op.name = name
    return op


def _make_query_stats_response(stats):
    resp = MagicMock()
    resp.output_port_query_stats_responses = stats
    return resp


@patch("app.mcp.mcp.get_db_session")
@patch("app.mcp.mcp.get_access_token")
@patch("app.mcp.mcp.get_mcp_authenticated_user")
@patch("app.mcp.mcp.DataProductService")
@patch("app.mcp.mcp.OutputPortCostService")
@patch("app.mcp.mcp.OutputPortService")
@patch("app.mcp.mcp.OutputPortStatsService")
class TestGetDataProductUsage:
    def _setup_mocks(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
        cost_rows=None,
        output_ports=None,
        query_stats_by_port=None,
        data_product=None,
    ):
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}

        dp = data_product or MagicMock()
        mock_dp_svc_cls.return_value.get_data_product.return_value = dp

        mock_cost_svc_cls.return_value.get_data_product_cost_summary.return_value = (
            cost_rows or []
        )
        mock_output_port_svc_cls.return_value.get_output_ports.return_value = (
            output_ports or []
        )

        def get_query_stats_side_effect(dataset_id, granularity, day_range):
            return (query_stats_by_port or {}).get(
                dataset_id, _make_query_stats_response([])
            )

        mock_stats_svc_cls.return_value.get_query_stats.side_effect = (
            get_query_stats_side_effect
        )

    def test_returns_cost_summary_for_single_output_port(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Cost summary aggregates correctly for one output port."""
        cost_rows = [
            _make_cost_row(OUTPUT_PORT_ID_A, "Port A", "80.00", "40.00", "30.00")
        ]
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            cost_rows=cost_rows,
            output_ports=[],
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert "error" not in result
        assert result["data_product_id"] == DATA_PRODUCT_ID
        assert result["day_range"] == 30
        cs = result["cost_summary"]
        assert cs["total_cost"] == 150.0
        assert len(cs["by_output_port"]) == 1
        port = cs["by_output_port"][0]
        assert port["output_port_id"] == str(OUTPUT_PORT_ID_A)
        assert port["output_port_name"] == "Port A"
        assert port["compute_cost"] == 80.0
        assert port["storage_cost"] == 40.0
        assert port["platform_overhead_cost"] == 30.0
        assert port["total_cost"] == 150.0

    def test_returns_cost_summary_for_multiple_output_ports(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Total cost is sum across all output ports."""
        cost_rows = [
            _make_cost_row(OUTPUT_PORT_ID_A, "Port A", "80.00", "40.00", "30.00"),
            _make_cost_row(OUTPUT_PORT_ID_B, "Port B", "50.00", "20.00", "20.00"),
        ]
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            cost_rows=cost_rows,
            output_ports=[],
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert result["cost_summary"]["total_cost"] == 240.0
        assert len(result["cost_summary"]["by_output_port"]) == 2

    def test_consumer_query_stats_aggregated_per_output_port(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Query counts are summed per consumer across all days for each output port."""
        port_a = _make_output_port(OUTPUT_PORT_ID_A, "Port A")
        stats_a = _make_query_stats_response([
            _make_stat("2026-04-01", CONSUMER_ID_1, "Consumer One", 100),
            _make_stat("2026-04-02", CONSUMER_ID_1, "Consumer One", 200),
            _make_stat("2026-04-01", CONSUMER_ID_2, "Consumer Two", 50),
        ])
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            output_ports=[port_a],
            query_stats_by_port={OUTPUT_PORT_ID_A: stats_a},
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        qs = result["consumer_query_stats"]
        assert len(qs) == 1
        port_stats = qs[0]
        assert port_stats["output_port_id"] == str(OUTPUT_PORT_ID_A)
        assert port_stats["output_port_name"] == "Port A"
        consumers = port_stats["top_consumers"]
        # Consumer One has 300 total, Consumer Two has 50 — sorted descending
        assert len(consumers) == 2
        assert consumers[0]["consumer_data_product_name"] == "Consumer One"
        assert consumers[0]["total_queries"] == 300
        assert consumers[1]["consumer_data_product_name"] == "Consumer Two"
        assert consumers[1]["total_queries"] == 50

    def test_data_product_not_found_returns_error(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """Returns error dict when data product does not exist."""
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            data_product=None,
        )
        mock_dp_svc_cls.return_value.get_data_product.return_value = None

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert "error" in result
        assert DATA_PRODUCT_ID in result["error"]

    def test_day_range_forwarded_to_services(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """day_range parameter is passed through to both cost and query stats services."""
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
        )

        result = get_data_product_usage(DATA_PRODUCT_ID, day_range=90)

        assert result["day_range"] == 90
        mock_cost_svc_cls.return_value.get_data_product_cost_summary.assert_called_once()
        call_args = mock_cost_svc_cls.return_value.get_data_product_cost_summary.call_args
        assert call_args[0][1] == 90 or call_args[1].get("day_range") == 90

    def test_no_data_returns_empty_collections(
        self,
        mock_stats_svc_cls,
        mock_output_port_svc_cls,
        mock_cost_svc_cls,
        mock_dp_svc_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """When there are no cost records or output ports, returns zeros and empty lists."""
        self._setup_mocks(
            mock_stats_svc_cls,
            mock_output_port_svc_cls,
            mock_cost_svc_cls,
            mock_dp_svc_cls,
            mock_get_user,
            mock_get_token,
            mock_get_db,
            cost_rows=[],
            output_ports=[],
        )

        result = get_data_product_usage(DATA_PRODUCT_ID)

        assert "error" not in result
        assert result["cost_summary"]["total_cost"] == 0.0
        assert result["cost_summary"]["by_output_port"] == []
        assert result["consumer_query_stats"] == []
```

- [ ] **Step 2: Run the tests to verify they fail**

```bash
cd backend && poetry run pytest tests/app/mcp/test_get_data_product_usage.py -v
```

Expected: `ImportError` or `AttributeError` — `get_data_product_usage` does not exist yet.

---

## Task 2: Implement `get_data_product_usage` in `mcp.py`

**Files:**
- Modify: `backend/app/mcp/mcp.py`

- [ ] **Step 1: Add imports at the top of `mcp.py`**

After the existing import block (around line 50), add:

```python
from decimal import Decimal

from app.data_products.output_ports.cost.service import OutputPortCostService
from app.data_products.output_ports.query_stats.service import (
    OutputPortStatsService,
    QueryStatsGranularity,
)
```

Exact insertion point — after this existing line:
```python
from app.data_products.output_ports.service import OutputPortService
```

Add the three new imports below it.

- [ ] **Step 2: Add the tool function**

Insert the new tool in the `DETAILED ENTITY INFORMATION` section, after `get_data_product_analytics` (around line 609 in the original file). Add:

```python
@mcp.tool
def get_data_product_usage(data_product_id: str, day_range: int = 30) -> Dict[str, Any]:
    """
    Get cost breakdown and consumer query stats for a data product over a configurable
    time window. Use this to answer questions like 'what did X cost last month?' or
    'which teams query this data product most?'.

    Cost is broken down per output port. Consumer query stats are also per output port,
    with a ranked list of consumer data products by total query count.

    Args:
        data_product_id: UUID obtained from search_data_products or get_data_product_details.
        day_range: Number of days to look back (default 30).
    """
    try:
        db = next(get_db_session())
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            data_product = DataProductService(db).get_data_product(
                id=UUID(data_product_id)
            )
            if not data_product:
                return {"error": f"Data product {data_product_id} not found"}

            # Cost summary aggregated across all output ports
            cost_rows = OutputPortCostService(db).get_data_product_cost_summary(
                UUID(data_product_id), day_range
            )
            cost_by_port = []
            total_cost = Decimal(0)
            for row in cost_rows:
                row_total = (
                    row.compute_cost + row.storage_cost + row.platform_overhead_cost
                )
                total_cost += row_total
                cost_by_port.append(
                    {
                        "output_port_id": str(row.output_port_id),
                        "output_port_name": row.output_port_name,
                        "compute_cost": float(row.compute_cost),
                        "storage_cost": float(row.storage_cost),
                        "platform_overhead_cost": float(row.platform_overhead_cost),
                        "total_cost": float(row_total),
                    }
                )

            # Per-output-port consumer query stats
            output_ports = OutputPortService(db).get_output_ports(
                user=user, data_product_id=UUID(data_product_id)
            )
            consumer_query_stats = []
            for op in output_ports:
                stats_response = OutputPortStatsService(db).get_query_stats(
                    dataset_id=op.id,
                    granularity=QueryStatsGranularity.DAY,
                    day_range=day_range,
                )
                consumer_totals: Dict[str, Any] = {}
                for stat in stats_response.output_port_query_stats_responses:
                    consumer_id = str(stat.consumer_data_product_id)
                    if consumer_id not in consumer_totals:
                        consumer_totals[consumer_id] = {
                            "consumer_data_product_id": consumer_id,
                            "consumer_data_product_name": stat.consumer_data_product_name,
                            "total_queries": 0,
                        }
                    consumer_totals[consumer_id]["total_queries"] += stat.query_count

                top_consumers = sorted(
                    consumer_totals.values(),
                    key=lambda c: c["total_queries"],
                    reverse=True,
                )
                consumer_query_stats.append(
                    {
                        "output_port_id": str(op.id),
                        "output_port_name": op.name,
                        "top_consumers": top_consumers,
                    }
                )

            return {
                "data_product_id": data_product_id,
                "day_range": day_range,
                "cost_summary": {
                    "total_cost": float(total_cost),
                    "by_output_port": cost_by_port,
                },
                "consumer_query_stats": consumer_query_stats,
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data product usage: {str(e)}"}
```

- [ ] **Step 3: Update the MCP `instructions` string**

Find the existing `instructions` block in the `FastMCP(...)` constructor (around line 73). Add a line about `get_data_product_usage`:

Replace:
```python
    instructions="""
    Portal for discovering and exploring data products and output ports.

    Recommended discovery flow:
    1. get_marketplace_overview: understand what's available and get domain IDs
    2. search_output_ports: find specific output ports (preferred for most searches)
       Use search_data_products only when the user explicitly asks to find a data product.
    3. get_*_details: drill into a specific result by UUID

    Output ports (datasets) are the primary way data is shared in the portal.
    Data products are containers owned by teams that group related output ports and technical assets.
    """,
```

With:
```python
    instructions="""
    Portal for discovering and exploring data products and output ports.

    Recommended discovery flow:
    1. get_marketplace_overview: understand what's available and get domain IDs
    2. search_output_ports: find specific output ports (preferred for most searches)
       Use search_data_products only when the user explicitly asks to find a data product.
    3. get_*_details: drill into a specific result by UUID
    4. get_data_product_usage: get cost breakdown and top consumer query stats for a data product

    Output ports (datasets) are the primary way data is shared in the portal.
    Data products are containers owned by teams that group related output ports and technical assets.
    """,
```

- [ ] **Step 4: Run the tests**

```bash
cd backend && poetry run pytest tests/app/mcp/test_get_data_product_usage.py -v
```

Expected: All 6 tests pass.

- [ ] **Step 5: Run the full backend test suite to check for regressions**

```bash
cd backend && poetry run pytest -v --tb=short
```

Expected: All tests pass.

- [ ] **Step 6: Run linting and type checking**

```bash
cd backend && poetry run ruff check app/mcp/mcp.py && poetry run ruff format --check app/mcp/mcp.py
```

Expected: No errors.

```bash
cd backend && poetry run mypy app/mcp/mcp.py
```

Expected: No errors (or only pre-existing errors unrelated to this change).

- [ ] **Step 7: Commit**

```bash
git add backend/app/mcp/mcp.py backend/tests/app/mcp/test_get_data_product_usage.py
git commit -m "feat(mcp): add get_data_product_usage tool for cost and consumer query stats"
```
