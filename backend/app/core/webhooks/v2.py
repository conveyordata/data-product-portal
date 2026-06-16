import uuid
from datetime import datetime, timezone

import httpx

from app.core.logging import logger
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
            resp.raise_for_status()
    except Exception as e:
        logger.warning("v2 webhook failed: %s", e)
