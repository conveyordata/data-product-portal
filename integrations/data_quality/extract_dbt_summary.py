import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATUS_PRIORITY = {
    "pass": 0,
    "fail": 1,
    "warning": 2,
    "error": 3,
}

DBT_TO_PORT_STATUS = {
    "success": "pass",
    "warn": "warning",
    "error": "error",
    "fail": "fail",
}


def worst_status(statuses):
    """Return the worst status based on priority."""
    return max(statuses, key=lambda s: STATUS_PRIORITY[s])


def load_dbt_results(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def extract_assets(dbt_results: dict) -> list[dict]:
    assets = []

    for result in dbt_results.get("results", []):
        unique_id = result.get("unique_id", "")
        asset_name = unique_id.split(".")[-1]

        dbt_status = result.get("status", "unknown")
        port_status = DBT_TO_PORT_STATUS.get(dbt_status, "unknown")

        assets.append(
            {
                "name": asset_name,
                "status": port_status,
            }
        )

    return assets


def build_output_port_summary(
    dbt_results: dict,
    details_url: str,
    summary: str | None = None,
) -> dict:
    assets = extract_assets(dbt_results)
    asset_statuses = [a["status"] for a in assets]

    overall_status = worst_status(asset_statuses)

    return {
        "created_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "overall_status": overall_status,
        "summary": summary or "dbt run results summary",
        "technical_assets": assets,
        "dimensions": {},
        "details_url": details_url,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python soda_to_output_port.py <dbt_results.json>")
        sys.exit(1)

    dbt_results_path = Path(sys.argv[1])
    details_url = "https://github.com/datamindedbe/conveyor/actions/runs/123"

    dbt_results = load_dbt_results(dbt_results_path)

    output_port_summary = build_output_port_summary(
        dbt_results,
        details_url=details_url,
        summary="dbt run completed successfully",
    )

    print(json.dumps(output_port_summary, indent=2))
