import re
from collections import defaultdict

from fastapi import HTTPException


def _to_example_key(detail: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", detail.lower()).strip("_")
    return key or "error"


def process_errors_as_route_responses(errors: list[HTTPException]) -> dict[int, dict]:
    errors_by_status = defaultdict(list)
    for error in errors:
        errors_by_status[error.status_code].append(error)

    responses: dict[int, dict] = {}
    for status_code, status_errors in errors_by_status.items():
        details = [str(error.detail) for error in status_errors]
        if len(details) == 1:
            detail = details[0]
            responses[status_code] = {
                "description": detail,
                "content": {"application/json": {"example": {"detail": detail}}},
            }
            continue

        examples: dict[str, dict] = {}
        key_count: dict[str, int] = {}
        for detail in details:
            base_key = _to_example_key(detail)
            key_count[base_key] = key_count.get(base_key, 0) + 1
            key = (
                base_key
                if key_count[base_key] == 1
                else f"{base_key}_{key_count[base_key]}"
            )
            examples[key] = {"value": {"detail": detail}}

        responses[status_code] = {
            "description": "Possible errors",
            "content": {"application/json": {"examples": examples}},
        }

    return responses
