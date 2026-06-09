import uuid
from collections.abc import AsyncGenerator, Callable
from datetime import datetime, timezone

import httpx
from fastapi import Request

from app.core.logging import logger
from app.core.webhooks.events import V2Event
from app.settings import settings

_MISSING = object()


async def call_v2_webhook(event_type: str, data: dict) -> None:
    if not (url := settings.WEBHOOK_V2_URL):
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
            resp = await client.post(url, json=body, timeout=5.0)
            if resp.status_code != 200:
                logger.warning("v2 webhook returned %d", resp.status_code)
    except Exception as e:
        logger.warning("v2 webhook failed: %s", e)


def _emits_event(
    event_model: type[V2Event],
) -> Callable[[Request], AsyncGenerator[None, None]]:
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
