"""Boundary around calls into plugin code.

A plugin runs inside the portal's own process, so an uncaught exception from one
plugin would otherwise fail the request handling it. Catch it, log it with its
stack trace, and turn it into a clean error for the caller.

See docs/adr/0024-dynamic-plugin-system.md.
"""

from typing import Any, Callable

from fastapi import HTTPException, status

from app.core.logging import logger


def call_plugin(
    plugin_name: str,
    method_name: str,
    call: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Any:
    try:
        return call(*args, **kwargs)
    except (NotImplementedError, HTTPException):
        # Both are part of the plugin API rather than failures: NotImplementedError
        # is how a plugin says it does not offer this method, and an HTTPException
        # is a status the plugin picked on purpose. Let them through.
        raise
    except Exception:
        logger.exception(f"Plugin '{plugin_name}' raised in '{method_name}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plugin '{plugin_name}' failed to handle this request",
        )
