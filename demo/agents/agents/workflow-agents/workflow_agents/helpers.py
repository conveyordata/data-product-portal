"""Shared helper utilities for workflow agents."""

from __future__ import annotations

import re
from typing import Any


def _fuzzy_match(
    name: str, items: list[dict[str, Any]], key: str = "name"
) -> dict[str, Any] | None:
    """Case-insensitive substring match on items."""
    name_lower = name.lower().strip()
    for item in items:
        if (item.get(key) or "").lower().strip() == name_lower:
            return item
    # Partial match fallback
    for item in items:
        if name_lower in (item.get(key) or "").lower():
            return item
    return None


def _format_ports_list(ports: list[dict[str, Any]]) -> str:
    lines = ["Here are the available output ports that match your use-case:\n"]
    for i, p in enumerate(ports, 1):
        dp_name = (
            p.get("data_product_name")
            or (p.get("data_product") or {}).get("name", "Unknown")
            or "Unknown"
        )
        access = p.get("access_type", "unknown")
        desc = p.get("description") or ""
        lines.append(
            f"{i}. **{p.get('name')}** (from *{dp_name}*) — {desc} [access: {access}]"
        )
    lines.append(
        "\nWhich ones do you need access to? (list by number or name, or type 'none')"
    )
    return "\n".join(lines)


def _parse_user_selection(
    user_input: str,
    presented_ports: list[dict[str, Any]],
) -> list[str]:
    """Parse user selection text → list of dataset IDs."""
    text = (user_input or "").lower().strip()
    if text in ("none", "no", "skip", "n/a", "0"):
        return []

    # "all/every/each" takes priority over any numeric extraction
    if any(w in text for w in ("all", "every", "each")):
        return [p["id"] for p in presented_ports]

    selected_ids: list[str] = []
    # Try numeric indices
    numbers = re.findall(r"\b(\d+)\b", text)
    for n in numbers:
        idx = int(n) - 1
        if 0 <= idx < len(presented_ports):
            selected_ids.append(presented_ports[idx]["id"])

    # Try name matches
    for p in presented_ports:
        name_lower = (p.get("name") or "").lower()
        if name_lower and name_lower in text:
            if p["id"] not in selected_ids:
                selected_ids.append(p["id"])

    return selected_ids


def _parse_requirements_json(text: str) -> dict[str, Any] | None:
    """Extract the REQUIREMENTS_COMPLETE JSON block from agent output."""
    import json

    match = re.search(
        r"REQUIREMENTS_COMPLETE\s*```(?:json)?\s*(\{.*?\})\s*```",
        text,
        re.DOTALL,
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
