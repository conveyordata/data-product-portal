import json

import httpx

from app.core.logging.logger import logger
from app.settings import settings


async def call_webhook(content, method, url, query, body=None):
    webhook_url = settings.WEBHOOK_URL
    async with httpx.AsyncClient() as client:
        content = {
            "method": method,
            "url": url,
            "query": query,
            # "body": body if body else {},
            # Body is behaving weirdly. Not sure if needed here?
            "response": content,
        }
        logger.info("Webhook triggered with content: %s", content)
        resp = await client.post(webhook_url, json=json.dumps(content))
        if (resp.status_code != 200) or (resp.json().get("status") != "ok"):
            logger.warning(f"Failed to send notification to {webhook_url}")
