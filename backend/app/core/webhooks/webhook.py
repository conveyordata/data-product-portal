import hashlib
import hmac
import json
from typing import Annotated, Literal, Union

import httpx
from fastapi import FastAPI
from pydantic import Field, create_model

from app.core.logging import logger
from app.core.webhooks.events import V2Event
from app.settings import settings


async def call_webhook(
    content: str, method: str, url: str, query: str, status_code: int
) -> None:
    webhook_url = settings.WEBHOOK_URL
    try:
        async with httpx.AsyncClient() as client:
            message = {
                "method": method,
                "url": url,
                "query": query,
                "response": content,
                "status_code": status_code,
            }
            logger.info("Webhook triggered with content: %s", message)

            headers = {}
            if settings.WEBHOOK_SECRET:
                headers = {
                    "Sign": hmac.new(
                        bytes(settings.WEBHOOK_SECRET, encoding="utf-8"),
                        bytes(json.dumps(message), encoding="utf-8"),
                        digestmod=hashlib.sha512,
                    ).hexdigest()
                }

            resp = await client.post(webhook_url, json=message, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"Failed to send notification to {webhook_url}")
    except Exception as e:
        logger.warning(f"Failed to send notification to {webhook_url}", e)


def register_webhooks(app: FastAPI) -> None:
    """Dynamically registers a single unified V2 events webhook into the FastAPI OpenAPI spec endpoint,
    displaying a union of all events.
    """
    event_models = []

    # Dynamically generate individual CloudEvent models
    for cls in V2Event.__subclasses__():
        event_type = cls.event_type()

        # Using Literal[event_type] forces Pydantic to treat this field as a unique constant tag
        CloudEventModel = create_model(
            f"CloudEvent_{cls.__name__}",
            specversion=(
                str,
                Field(
                    default="1.0", description="The CloudEvents specification version."
                ),
            ),
            id=(
                str,
                Field(
                    ...,
                    description="A unique UUID identifier for this specific event instance.",
                ),
            ),
            source=(
                str,
                Field(
                    default="data-product-portal",
                    description="Identifies the context in which an event happened.",
                ),
            ),
            type=(
                Literal[event_type],
                Field(
                    default=event_type,
                    description="The unique type string belonging to this event.",
                ),
            ),
            time=(
                str,
                Field(
                    ...,
                    description="Timestamp of when the event occurred in ISO 8601 UTC format.",
                ),
            ),
            data=(
                cls,
                Field(
                    ...,
                    description="The specific data payload corresponding to this event type.",
                ),
            ),
        )
        event_models.append(CloudEventModel)

    if not event_models:
        return

    # Programmatically construct a Discriminated Union across all event shapes
    # Subscripting Union with a tuple builds a dynamic Union over all classes
    V2EventUnion = Union[tuple(event_models)]  # type: ignore[valid-type]
    UnifiedWebhookPayload = Annotated[V2EventUnion, Field(discriminator="type")]  # type: ignore[valid-type]

    # Define a single handler for the event stream
    async def v2_webhook_stream_handler(body: UnifiedWebhookPayload) -> None:
        pass

    # Register the single route definition
    app.webhooks.post(
        path="v2_event_stream",
        summary="Event Stream Webhook",
        operation_id="event_stream",
        description=(
            "The primary webhook subscription target."
            "Receives a real-time event stream wrapped in a CloudEvents 1.0 envelope."
            "Inspect the `type` field to distinguish between payload formats."
        ),
    )(v2_webhook_stream_handler)
