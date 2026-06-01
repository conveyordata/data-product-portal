"""Typed Pydantic models for each v2 webhook event payload."""

from typing import Any, ClassVar

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


# ---------------------------------------------------------------------------
# Data Product events
# ---------------------------------------------------------------------------


class DataProductCreatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.created"

    data_product: GetDataProductResponse


class DataProductUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.updated"

    data_product: GetDataProductResponse


class DataProductDeletedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.deleted"

    data_product: GetDataProductResponse


class DataProductAboutUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.about_updated"

    data_product: GetDataProductResponse


class DataProductStatusUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.status_updated"

    data_product: GetDataProductResponse


class DataProductSettingChangedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.setting_changed"

    data_product: GetDataProductResponse


class DataProductInputPortLinkedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.input_port_linked"

    data_product: GetDataProductResponse


class DataProductInputPortUnlinkedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.input_port_unlinked"

    data_product: GetDataProductResponse


class DataProductTeamMemberAddedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.team_member_added"

    data_product: GetDataProductResponse


class DataProductTeamMemberRemovedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.team_member_removed"

    data_product: GetDataProductResponse


class DataProductTeamMemberUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "data_product.team_member_updated"

    data_product: GetDataProductResponse


# ---------------------------------------------------------------------------
# Output Port events
# ---------------------------------------------------------------------------


class OutputPortCreatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.created"

    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.updated"

    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortDeletedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.deleted"

    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortAboutUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.about_updated"

    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortStatusUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.status_updated"

    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortSettingChangedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.setting_changed"

    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortLinkApprovedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.link_approved"

    abstract_data_product: GetAbstractDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortLinkDeniedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "output_port.link_denied"

    abstract_data_product: GetAbstractDataProductResponse
    output_port: GetOutputPortResponse


# ---------------------------------------------------------------------------
# Technical Asset events
# ---------------------------------------------------------------------------


class TechnicalAssetCreatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.created"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.updated"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetDeletedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.deleted"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetStatusUpdatedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.status_updated"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetLinkedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.linked"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetLinkApprovedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.link_approved"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetLinkDeniedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.link_denied"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetUnlinkedEvent(V2Event):
    @classmethod
    def event_type(cls) -> str:
        return "technical_asset.unlinked"

    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem
