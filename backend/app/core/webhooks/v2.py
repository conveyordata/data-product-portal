import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.logging import logger
from app.core.webhooks.events import V2Event
from app.database.database import get_db_session
from app.settings import settings
from app.users.schema import User

_MISSING = object()


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


def _emits_event(event_model: type[V2Event]) -> Callable:
    """Yield-based dependency factory that emits a V2 webhook after the handler succeeds.

    The handler is responsible for constructing the event and storing it on
    ``request.state.event``.  This dependency reads it after a successful
    response, validates the type, and calls the webhook.

    Raises ``RuntimeError`` if the handler did not set ``request.state.event``.
    Raises ``TypeError`` if the stored event is not an instance of ``event_model``.
    Webhook emission failures are logged but do not fail the HTTP response.
    """

    async def dependency(request: Request) -> AsyncGenerator[None, None]:
        try:
            yield
        except Exception:
            raise  # handler failed — never emit
        else:
            event = getattr(request.state, "event", _MISSING)
            if event is _MISSING:
                raise RuntimeError(
                    f"Handler did not set request.state.event "
                    f"(expected {event_model.__name__})"
                )
            if not isinstance(event, event_model):
                raise TypeError(
                    f"Expected {event_model.__name__} on request.state.event, "
                    f"got {type(event).__name__}"
                )
            try:
                if settings.WEBHOOK_V2_URL:
                    await call_v2_webhook(
                        event_model.event_type(), event.model_dump(mode="json")
                    )
            except Exception as e:
                logger.warning("v2 webhook emit failed: %s", e)

    # Preserve metadata consumed by webhook_doc_export.py
    dependency._webhook_event_type = event_model.event_type()  # type: ignore[attr-defined]
    dependency._webhook_payload_model = event_model  # type: ignore[attr-defined]
    return dependency


def emit_event(event_type: str, event_model: type, extract: Any) -> Callable:
    """
    Dependency factory for DELETE routes.

    Runs before the handler. Fetches objects via `extract`, schedules
    `call_v2_webhook` as a background task. Starlette discards background
    tasks when the handler raises HTTPException, so the webhook never fires
    on failure.
    """

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
    _dependency._webhook_payload_model = event_model  # type: ignore[attr-defined]
    return _dependency


def emit_event_after(event_type: str, event_model: type, extract: Any) -> Callable:
    """
    Yield-based dependency factory for CREATE and UPDATE routes.

    The `else` branch of try/except/else only runs when the handler returned
    normally — any exception raised by the handler re-raises in `except`,
    skipping the else block, so the webhook never fires on failure.
    """

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
    _dependency._webhook_payload_model = event_model  # type: ignore[attr-defined]
    return _dependency
