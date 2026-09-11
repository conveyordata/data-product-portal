"""Call-boundary wrapper for calling into a plugin's code.

Per the ADR: an uncaught exception from a plugin is caught, logged with its
stack trace, and surfaced as a clean error - one broken plugin can't take
down the request it's handling.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

from app.core.logging import logger


@dataclass
class PluginCallResult:
    ok: bool
    value: Any = None
    error: Optional[str] = None


def call_plugin(
    plugin_key: str, method_name: str, fn: Callable[..., Any], *args: Any, **kwargs: Any
) -> PluginCallResult:
    try:
        return PluginCallResult(ok=True, value=fn(*args, **kwargs))
    except Exception:
        logger.exception(
            f"Plugin '{plugin_key}' raised in '{method_name}'",
        )
        return PluginCallResult(
            ok=False, error=f"Plugin '{plugin_key}' failed to handle this request"
        )
