"""
Spike for ADR-0024: a plugin as one class carrying both its declarative
description (fields, environment_fields, icon, ...) and its behavior
(validate, render_result, get_url, is_shareable).

Not wired into the real technical-asset-configuration system. See
docs/adr/0024-dynamic-plugin-system.md.
"""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class SpikeAssetPlugin(BaseModel):
    """Base class a plugin inherits from. Instances are built directly from
    whatever dict is stored in the JSONB config column, and Pydantic does the
    real validation (required fields, types, extra="forbid") against the
    plugin's own declared fields -- not against a database schema."""

    model_config = ConfigDict(extra="forbid")

    # --- declarative part ---
    key: ClassVar[str]
    display_name: ClassVar[str]
    icon: ClassVar[str] = ""
    group: ClassVar[str | None] = None
    # Same idea as `fields`, one level up: what an environment needs to
    # provide for this plugin. Enforced the same way -- Pydantic model,
    # not a table -- see the *EnvironmentConfig classes below.
    environment_fields: ClassVar[type[BaseModel]]

    # --- behavior part ---
    def validate_configuration(self, *, namespace: str | None = None) -> None:
        """Cross-field / contextual validation beyond plain field types.
        Default: nothing extra. Override per plugin (e.g. Glue's namespace check)."""
        return None

    def render_result(self, environment_config: dict[str, Any]) -> str:
        raise NotImplementedError

    def get_url(self, environment_config: dict[str, Any]) -> str:
        raise NotImplementedError

    def is_shareable(self) -> bool:
        """Hook for the (out of scope, not implemented here) 'unshareable
        asset types' request. Default: yes."""
        return True
