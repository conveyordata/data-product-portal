"""Generic response shapes for dynamic plugin discovery.

`fields` is `list[dict[str, Any]]` - not a per-plugin typed model. The
published OpenAPI schema (and therefore the generated frontend client,
Python SDK, and Go CLI) describes a plugin's fields the same way for every
plugin, built-in or custom, regardless of which plugins happen to be
installed at core-project release time. See ADR-0024, "How the API
describes a plugin's configuration".
"""

from typing import Any

from pydantic import BaseModel


class PluginSummary(BaseModel):
    key: str
    display_name: str
    fields: list[dict[str, Any]]


class PluginListResponse(BaseModel):
    plugins: list[PluginSummary]
