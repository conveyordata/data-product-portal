import json

import httpx

from app.core.logging.logger import logger
from app.settings import settings


async def call_webhook(content, method, url, query, status_code):
    webhook_url = settings.WEBHOOK_URL
    if webhook_url:
        try:
            async with httpx.AsyncClient() as client:
                content = {
                    "method": method,
                    "url": url,
                    "query": query,
                    "response": content,
                    "status_code": status_code,
                }
                logger.info("Webhook triggered with content: %s", content)
                resp = await client.post(webhook_url, json=json.dumps(content))
                if (resp.status_code != 200) or (resp.json().get("status") != "ok"):
                    logger.warning(f"Failed to send notification to {webhook_url}")
        except Exception as e:
            logger.warning(f"Failed to send notification to {webhook_url}", e)
