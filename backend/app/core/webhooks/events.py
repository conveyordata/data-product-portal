"""Typed Pydantic models for each v2 webhook event payload."""

from typing import Any, ClassVar
from uuid import UUID

from pydantic import BaseModel

from app.abstract_data_product.type import AbstractDataProductType


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


class ExplorationEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "exploration.event"

    id: UUID


class DataProductEvent(V2Event):
    id: UUID

    @classmethod
    def event_type(cls) -> str:
        return "data_product.event"


class InputPortEvent(V2Event):
    id: UUID
    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product_type: AbstractDataProductType

    @classmethod
    def event_type(cls) -> str:
        return "input_port.event"


class DataProductRoleAssignmentEvent(V2Event):
    """Fired on insert, update, and delete of a data-product role assignment."""

    id: UUID
    data_product_id: UUID
    user_id: UUID

    @classmethod
    def event_type(cls) -> str:
        return "data_product.role_assignment.event"


class OutputPortRoleAssignmentEvent(V2Event):
    """Fired on insert, update, and delete of an output-port role assignment."""

    id: UUID
    output_port_id: UUID
    data_product_id: UUID
    user_id: UUID

    @classmethod
    def event_type(cls) -> str:
        return "output_port.role_assignment.event"
