import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.logging import logger
from app.database.database import get_db_session
from app.settings import settings
from app.users.schema import User


async def call_v2_webhook(event_type: str, data: dict) -> None:
    url = settings.WEBHOOK_V2_URL
    if not url:
        return
    body = {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "data-product-portal",
        "type": event_type,
        "time": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=body)
            if resp.status_code != 200:
                logger.warning("v2 webhook returned %d", resp.status_code)
    except Exception as e:
        logger.warning("v2 webhook failed: %s", e)


def emit_event(
    event_type: str, event_model_or_extract: Any, extract: Any = None
) -> Callable:
    """
    Dependency factory for DELETE routes.

    Runs before the handler. Fetches objects via `extract`, schedules
    `call_v2_webhook` as a background task. Starlette discards background
    tasks when the handler raises HTTPException, so the webhook never fires
    on failure.

    Signature supports both:
    - New: emit_event(event_type, event_model, extract)
    - Legacy: emit_event(event_type, extract)
    """
    # Handle overloading: if extract is None, event_model_or_extract is the extract function
    if extract is None:
        extract = event_model_or_extract
        event_model = None
    else:
        event_model = event_model_or_extract

    async def _dependency(
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db_session),
        authenticated_user: User = Depends(get_authenticated_user),
    ) -> None:
        try:
            if not settings.WEBHOOK_V2_URL:
                return
            result = extract(
                request=request,
                db=db,
                authenticated_user=authenticated_user,
                **request.path_params,
            )
            data = {k: v.model_dump(mode="json") for k, v in result.items()}
            background_tasks.add_task(call_v2_webhook, event_type, data)
        except Exception as e:
            logger.warning("v2 webhook setup failed: %s", e)

    _dependency._webhook_event_type = event_type  # type: ignore[attr-defined]
    if event_model is not None:
        _dependency._webhook_payload_model = event_model  # type: ignore[attr-defined]
    return _dependency


def emit_event_after(
    event_type: str, event_model_or_extract: Any, extract: Any = None
) -> Callable:
    """
    Yield-based dependency factory for CREATE and UPDATE routes.

    The `else` branch of try/except/else only runs when the handler returned
    normally — any exception raised by the handler re-raises in `except`,
    skipping the else block, so the webhook never fires on failure.

    Signature supports both:
    - New: emit_event_after(event_type, event_model, extract)
    - Legacy: emit_event_after(event_type, extract)
    """
    # Handle overloading: if extract is None, event_model_or_extract is the extract function
    if extract is None:
        extract = event_model_or_extract
        event_model = None
    else:
        event_model = event_model_or_extract

    async def _dependency(
        request: Request,
        db: Session = Depends(get_db_session),
        authenticated_user: User = Depends(get_authenticated_user),
    ) -> AsyncGenerator[None, None]:
        try:
            yield
        except Exception:
            raise
        else:
            try:
                if not settings.WEBHOOK_V2_URL:
                    return
                result = extract(
                    request=request,
                    db=db,
                    authenticated_user=authenticated_user,
                    **request.path_params,
                )
                data = {k: v.model_dump(mode="json") for k, v in result.items()}
                await call_v2_webhook(event_type, data)
            except Exception as e:
                logger.warning("v2 webhook emit failed: %s", e)

    _dependency._webhook_event_type = event_type  # type: ignore[attr-defined]
    if event_model is not None:
        _dependency._webhook_payload_model = event_model  # type: ignore[attr-defined]
    return _dependency
