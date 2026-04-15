"""Filter the full OpenAPI spec down to /api/v2/ paths only, pruning unused schemas."""

import json
import re
from pathlib import Path

INPUT = Path(__file__).parent.parent.parent / "docs" / "static" / "openapi.json"
OUTPUT = Path(__file__).parent.parent / "openapi-v2.json"


def collect_refs(obj: object, found: set[str]) -> None:
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref: str = obj["$ref"]
            match = re.match(r"#/components/schemas/(.+)", ref)
            if match:
                found.add(match.group(1))
        for value in obj.values():
            collect_refs(value, found)
    elif isinstance(obj, list):
        for item in obj:
            collect_refs(item, found)


def collect_all_refs(schemas: dict, seed: set[str]) -> set[str]:
    """Recursively follow $refs until the set stabilises."""
    collected = set(seed)
    while True:
        new_refs: set[str] = set()
        for name in collected:
            schema = schemas.get(name)
            if schema:
                collect_refs(schema, new_refs)
        added = new_refs - collected
        if not added:
            break
        collected |= added
    return collected


def main() -> None:
    with INPUT.open() as f:
        spec: dict = json.load(f)

    # Keep only /api/v2/ paths
    v2_paths = {
        k: v for k, v in spec.get("paths", {}).items() if k.startswith("/api/v2/")
    }
    spec["paths"] = v2_paths

    # Collect all schema names referenced by the kept paths
    seed: set[str] = set()
    collect_refs(v2_paths, seed)

    # Expand to include transitively referenced schemas
    all_schemas: dict = spec.get("components", {}).get("schemas", {})
    used = collect_all_refs(all_schemas, seed)

    # Prune unused schemas
    spec.setdefault("components", {})["schemas"] = {
        k: v for k, v in all_schemas.items() if k in used
    }

    with OUTPUT.open("w") as f:
        json.dump(spec, f, indent=2)

    print(f"Written {len(v2_paths)} paths and {len(used)} schemas to {OUTPUT}")


if __name__ == "__main__":
    main()
