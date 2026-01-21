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


def worst_status(statuses):
    return max(statuses, key=lambda s: STATUS_PRIORITY[s])


def load_soda_output(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def extract_assets(soda_output: dict) -> list[dict]:
    """
    One asset per table referenced in checks.
    """
    table_status: dict[str, list[str]] = {}

    for check in soda_output.get("checks", []):
        table = check.get("table", "unknown")
        outcome = check.get("outcome")

        if outcome == "fail":
            status = "fail"
        elif outcome == "warn":
            status = "warn"
        else:
            status = "pass"

        table_status.setdefault(table, []).append(status)

    assets = []
    for table, statuses in table_status.items():
        assets.append(
            {
                "name": table,
                "status": worst_status(statuses),
            }
        )

    return assets


def build_output_port_summary(
    soda_output: dict,
    details_url: str,
    summary: str | None = None,
) -> dict:
    assets = extract_assets(soda_output)
    asset_statuses = [a["status"] for a in assets]

    overall_status = worst_status(asset_statuses)

    return {
        "created_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "overall_status": overall_status,
        "summary": summary or "Soda data quality scan results",
        "technical_assets": assets,
        "dimensions": {},
        "details_url": details_url,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python soda_to_output_port.py <soda_results.json>")
        sys.exit(1)

    soda_results_path = Path(sys.argv[1])
    details_url = "https://ci.company.com/runs/456"

    soda_output = load_soda_output(soda_results_path)

    output_port_summary = build_output_port_summary(
        soda_output,
        details_url=details_url,
        summary="Soda scan completed with failed checks",
    )

    print(json.dumps(output_port_summary, indent=2))
