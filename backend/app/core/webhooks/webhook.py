from typing import Annotated, Literal, Union

from fastapi import FastAPI
from pydantic import Field, create_model

from app.core.webhooks.events import V2Event


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
