"""Typed Pydantic models for each v2 webhook event payload."""

from pydantic import BaseModel

from app.data_products.output_ports.schema_response import GetOutputPortResponse
from app.data_products.schema_response import GetDataProductResponse
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)

# ---------------------------------------------------------------------------
# Data Product events
# ---------------------------------------------------------------------------


class DataProductCreatedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductDeletedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductAboutUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductStatusUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductSettingChangedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductInputPortLinkedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductInputPortUnlinkedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductTeamMemberAddedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductTeamMemberRemovedEvent(BaseModel):
    data_product: GetDataProductResponse


class DataProductTeamMemberUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse


# ---------------------------------------------------------------------------
# Output Port events
# ---------------------------------------------------------------------------


class OutputPortCreatedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortDeletedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortAboutUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortStatusUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortSettingChangedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortLinkApprovedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


class OutputPortLinkDeniedEvent(BaseModel):
    data_product: GetDataProductResponse
    output_port: GetOutputPortResponse


# ---------------------------------------------------------------------------
# Technical Asset events
# ---------------------------------------------------------------------------


class TechnicalAssetCreatedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetDeletedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetStatusUpdatedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetLinkedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetLinkApprovedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetLinkDeniedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem


class TechnicalAssetUnlinkedEvent(BaseModel):
    data_product: GetDataProductResponse
    technical_asset: GetTechnicalAssetsResponseItem
