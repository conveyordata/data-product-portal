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
        raise
    except Exception:
        logger.exception(f"Plugin '{plugin_name}' raised in '{method_name}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plugin '{plugin_name}' failed to handle this request",
        )
