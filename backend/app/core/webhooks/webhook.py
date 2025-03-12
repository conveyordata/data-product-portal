import hashlib
import hmac
import json

import httpx

from app.core.logging.logger import logger
from app.settings import settings


async def call_webhook(content, method, url, query, status_code):
    webhook_url = settings.WEBHOOK_URL
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

            headers = {}
            if settings.WEBHOOK_SECRET:
                headers = {
                    "Sign": hmac.new(
                        bytes(settings.WEBHOOK_SECRET, encoding="utf-8"),
                        bytes(json.dumps(content), encoding="utf-8"),
                        digestmod=hashlib.sha512,
                    ).hexdigest()
                }

            resp = await client.post(webhook_url, json=content, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"Failed to send notification to {webhook_url}")
    except Exception as e:
        logger.warning(f"Failed to send notification to {webhook_url}", e)
