"""Typed Pydantic models for each v2 webhook event payload."""

from typing import Any, ClassVar
from uuid import UUID

from pydantic import BaseModel

from app.abstract_data_product.schema_response import GetAbstractDataProductResponse
from app.data_products.output_ports.schema_response import GetOutputPortResponse
from app.data_products.schema_response import GetDataProductResponse
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)


class V2Event(BaseModel):
    """Base class for all V2 webhook event payloads.

    Every subclass must define an ``event_type()`` classmethod that returns
    the CloudEvents ``type`` string.  Omitting it raises ``TypeError`` at
    class-definition time so mistakes are caught on import.
    """

    events: ClassVar[list[str]] = []

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "event_type" not in cls.__dict__:
            raise TypeError(f"{cls.__name__} must define an event_type() classmethod")
        if cls.event_type() in cls.events:
            raise Exception("Duplicated event type detected")
        cls.events.append(cls.event_type())

    @classmethod
    def event_type(cls) -> str:
        raise NotImplementedError


class ExplorationPayload(BaseModel):
    id: UUID


class ExplorationCreatedEvent(V2Event, ExplorationPayload):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.created"


class ExplorationUpdatedEvent(V2Event, ExplorationPayload):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.updated"


class ExplorationDeletedEvent(V2Event, ExplorationPayload):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.deleted"
