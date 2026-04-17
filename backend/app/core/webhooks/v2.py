import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone

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


def emit_event(event_type: str, extract) -> Callable:
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
        **kwargs,
    ) -> None:
        try:
            if not settings.WEBHOOK_V2_URL:
                return
            result = extract(
                request=request,
                db=db,
                authenticated_user=authenticated_user,
                **kwargs,
            )
            data = {k: v.model_dump(mode="json") for k, v in result.items()}
            background_tasks.add_task(call_v2_webhook, event_type, data)
        except Exception as e:
            logger.warning("v2 webhook setup failed: %s", e)

    return _dependency


def emit_event_after(event_type: str, extract) -> Callable:
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
        **kwargs,
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
                    **kwargs,
                )
                data = {k: v.model_dump(mode="json") for k, v in result.items()}
                await call_v2_webhook(event_type, data)
            except Exception as e:
                logger.warning("v2 webhook emit failed: %s", e)

    return _dependency
