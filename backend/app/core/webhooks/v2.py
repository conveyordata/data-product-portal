import uuid
from datetime import datetime, timezone
from typing import Sequence

import httpx

from app.core.logging import logger
from app.core.webhooks.events import V2Event
from app.settings import settings

_MISSING = object()


async def emit_all_events(events: Sequence[V2Event]) -> None:
    # Good for keeping sequential order, bad for speed, maybe also good for not DoSing the receiver.
    # To be checked if we ever run into issues with this.
    for event in events:
        await call_v2_webhook(type(event).event_type(), event.model_dump(mode="json"))


async def call_v2_webhook(event_type: str, data: dict) -> bool:
    if not (url := settings.WEBHOOK_V2_URL):
        return False
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
            resp.raise_for_status()
        return True
    except Exception as e:
        logger.warning("v2 webhook failed: %s", e)
        return False
