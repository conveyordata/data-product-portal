"""Typed Pydantic models for each v2 webhook event payload."""

from typing import Any, ClassVar
from uuid import UUID

from pydantic import BaseModel

from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


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


class Domain(ORMModel):
    id: UUID
    name: str


class ExplorationPayload(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str | None
    domain: Domain


class ExplorationCreatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.created"

    after: ExplorationPayload


class ExplorationUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.updated"

    before: ExplorationPayload
    after: ExplorationPayload


class ExplorationDeletedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.deleted"

    before: ExplorationPayload


class DataProductType(ORMModel):
    id: UUID
    name: str


class DataProductPayload(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str | None
    domain: Domain
    type: DataProductType
    status: DataProductStatus


class DataProductCreatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.created"

    after: DataProductPayload


class DataProductUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.updated"

    before: DataProductPayload
    after: DataProductPayload


class DataProductDeletedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.deleted"

    before: DataProductPayload
