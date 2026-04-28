# MCP Freshness Enrichment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose freshness status, SLO deadline, and last-refreshed timestamp inside `get_output_port_details` MCP tool responses.

**Architecture:** Enrich the existing `get_output_port_details` function in `mcp.py` by calling `FreshnessService` in the same DB session after the dataset is fetched, then merging a `freshness` block into the returned dict. No changes to REST schemas or service layer.

**Tech Stack:** Python, FastMCP, SQLAlchemy, pytest, `unittest.mock`

---

### Task 1: Write failing tests for freshness enrichment

**Files:**
- Create: `backend/tests/app/mcp/test_get_output_port_details_freshness.py`

- [ ] **Step 1: Write the three failing tests**

Create `backend/tests/app/mcp/test_get_output_port_details_freshness.py` with the following content:

```python
from datetime import UTC, datetime, time
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.mcp.mcp import get_output_port_details


OUTPUT_PORT_ID = str(uuid4())

_BASE_RESULT = {
    "id": OUTPUT_PORT_ID,
    "name": "my-output-port",
    "description": "desc",
}


def _mock_dataset():
    ds = MagicMock()
    ds.id = OUTPUT_PORT_ID
    return ds


def _mock_validated_response():
    mock = MagicMock()
    mock.model_dump.return_value = dict(_BASE_RESULT)
    return mock


@patch("app.mcp.mcp.get_db_session")
@patch("app.mcp.mcp.get_access_token")
@patch("app.mcp.mcp.get_mcp_authenticated_user")
@patch("app.mcp.mcp.OutputPortService")
@patch("app.mcp.mcp.GetOutputPortResponse")
@patch("app.mcp.mcp.FreshnessService")
class TestGetOutputPortDetailsFreshness:
    def test_freshness_with_slo_and_observation(
        self,
        mock_freshness_service_cls,
        mock_response_cls,
        mock_output_port_service_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """SLO configured + observation exists → freshness block with computed status."""
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}
        mock_output_port_service_cls.return_value.get_dataset.return_value = _mock_dataset()
        mock_response_cls.model_validate.return_value = _mock_validated_response()

        slo = MagicMock()
        slo.deadline_time = time(8, 0, 0)
        obs = MagicMock()
        obs.last_refreshed_at = datetime(2026, 4, 28, 7, 0, 0, tzinfo=UTC)
        obs.created_at = datetime(2026, 4, 28, 7, 0, 1, tzinfo=UTC)

        svc = mock_freshness_service_cls.return_value
        svc.get_slo.return_value = slo
        svc.get_latest_observation.return_value = obs
        svc.compute_status.return_value = FreshnessStatus.FRESH

        result = get_output_port_details(OUTPUT_PORT_ID)

        assert "freshness" in result
        f = result["freshness"]
        assert f["status"] == "fresh"
        assert f["slo_deadline"] == "08:00:00"
        assert f["last_refreshed_at"] == "2026-04-28T07:00:00+00:00"
        assert f["last_observed_at"] == "2026-04-28T07:00:01+00:00"

    def test_freshness_with_slo_no_observation(
        self,
        mock_freshness_service_cls,
        mock_response_cls,
        mock_output_port_service_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """SLO configured but no observations → status unknown, timestamps null."""
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}
        mock_output_port_service_cls.return_value.get_dataset.return_value = _mock_dataset()
        mock_response_cls.model_validate.return_value = _mock_validated_response()

        slo = MagicMock()
        slo.deadline_time = time(8, 0, 0)

        svc = mock_freshness_service_cls.return_value
        svc.get_slo.return_value = slo
        svc.get_latest_observation.return_value = None
        svc.compute_status.return_value = FreshnessStatus.UNKNOWN

        result = get_output_port_details(OUTPUT_PORT_ID)

        assert "freshness" in result
        f = result["freshness"]
        assert f["status"] == "unknown"
        assert f["slo_deadline"] == "08:00:00"
        assert f["last_refreshed_at"] is None
        assert f["last_observed_at"] is None

    def test_freshness_no_slo(
        self,
        mock_freshness_service_cls,
        mock_response_cls,
        mock_output_port_service_cls,
        mock_get_user,
        mock_get_token,
        mock_get_db,
    ):
        """No SLO configured → status unknown, all freshness fields null."""
        mock_get_db.return_value = iter([MagicMock()])
        mock_get_token.return_value = MagicMock(token="tok")
        mock_get_user.return_value = {"id": str(uuid4())}
        mock_output_port_service_cls.return_value.get_dataset.return_value = _mock_dataset()
        mock_response_cls.model_validate.return_value = _mock_validated_response()

        svc = mock_freshness_service_cls.return_value
        svc.get_slo.side_effect = HTTPException(status_code=404, detail="not found")

        result = get_output_port_details(OUTPUT_PORT_ID)

        assert "freshness" in result
        f = result["freshness"]
        assert f["status"] == "unknown"
        assert f["slo_deadline"] is None
        assert f["last_refreshed_at"] is None
        assert f["last_observed_at"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
poetry run pytest tests/app/mcp/test_get_output_port_details_freshness.py -v
```

Expected: 3 failures — `"freshness"` key not present in result.

---

### Task 2: Implement freshness enrichment in `mcp.py`

**Files:**
- Modify: `backend/app/mcp/mcp.py`

- [ ] **Step 3: Add imports**

At the top of `backend/app/mcp/mcp.py`, add these two imports alongside the existing ones:

```python
from fastapi import HTTPException

from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.data_products.output_ports.freshness.service import FreshnessService
```

- [ ] **Step 4: Enrich `get_output_port_details`**

Replace the body of `get_output_port_details` (currently lines ~395–411) so it reads:

```python
@mcp.tool
def get_output_port_details(output_port_id: str) -> Dict[str, Any]:
    """
    Get full details of a single output port by its UUID, including schema, access type,
    the data product it belongs to, owner contact information, and freshness status.
    Use after search_output_ports to get complete information about a specific dataset.

    Args:
        output_port_id: UUID obtained from search_output_ports or universal_search.
    """
    try:
        db = next(get_db_session())
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            dataset = OutputPortService(db).get_dataset(
                id=UUID(output_port_id), user=user
            )

            if not dataset:
                return {"error": f"Dataset {output_port_id} not found"}

            result = GetOutputPortResponse.model_validate(dataset).model_dump()

            freshness_service = FreshnessService(db)
            try:
                slo = freshness_service.get_slo(UUID(output_port_id))
                slo_deadline = str(slo.deadline_time)
            except HTTPException:
                slo = None
                slo_deadline = None

            latest_obs = freshness_service.get_latest_observation(UUID(output_port_id))
            status = (
                freshness_service.compute_status(dataset)
                if slo is not None
                else FreshnessStatus.UNKNOWN
            )

            result["freshness"] = {
                "status": status.value,
                "slo_deadline": slo_deadline,
                "last_refreshed_at": (
                    latest_obs.last_refreshed_at.isoformat() if latest_obs else None
                ),
                "last_observed_at": (
                    latest_obs.created_at.isoformat() if latest_obs else None
                ),
            }

            return result
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get dataset details: {str(e)}"}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd backend
poetry run pytest tests/app/mcp/test_get_output_port_details_freshness.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 6: Run the full test suite to check for regressions**

```bash
cd backend
poetry run pytest tests/ -x -q 2>&1 | tail -5
```

Expected: no new failures.

- [ ] **Step 7: Commit**

```bash
git add backend/app/mcp/mcp.py \
        backend/tests/app/mcp/test_get_output_port_details_freshness.py
git commit -m "feat(mcp): expose freshness data in get_output_port_details"
```
