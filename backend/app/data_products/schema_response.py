from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import Field

from app.abstract_data_product.schema_response import InputPort
from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import DataProductSettingValue
from app.configuration.data_product_types.schema import DataProductType
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_products.output_port_technical_assets_link.schema_response import (
    BaseTechnicalAssetOutputPortAssociationGet,
)
from app.data_products.status import AbstractDataProductStatus
from app.data_products.technical_assets.schema_response import (
    BaseTechnicalAssetGet,
)
from app.shared.schema import ORMModel


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    status: AbstractDataProductStatus
    finalizers: list[str]

    # Nested schemas
    tags: list[Tag]
    usage: Optional[str]
    domain: Domain
    type: DataProductType
    lifecycle: Optional[DataProductLifeCycle]


class TechnicalAssetLinks(BaseTechnicalAssetGet):
    # Nested schemas
    output_port_links: list[BaseTechnicalAssetOutputPortAssociationGet]


class GetDataProductResponse(BaseDataProductGet):
    about: Optional[str]


class GetDataProductSettingsResponse(ORMModel):
    data_product_settings: Sequence[DataProductSettingValue]


class GetDataProductInputPortsResponse(ORMModel):
    input_ports: Sequence[InputPort]


class GetDataProductRolledUpTagsResponse(ORMModel):
    rolled_up_tags: set[Tag]


class GetDataProductsResponseItem(BaseDataProductGet):
    user_count: int
    input_port_count: int
    technical_asset_count: int = Field(validation_alias="data_outputs_count")


@deprecated("Use LinkInputPortsToDataProductPost instead")
class LinkDatasetsToDataProductPost(ORMModel):
    dataset_links: list[UUID]


class LinkInputPortsToDataProductPost(ORMModel):
    input_port_links: list[UUID]


class RequestInputPortsForDataProductResponse(ORMModel):
    input_port_links: list[UUID]


class GetDataProductsResponse(ORMModel):
    data_products: Sequence[GetDataProductsResponseItem]


class CreateDataProductResponse(ORMModel):
    id: UUID


class UpdateDataProductResponse(ORMModel):
    id: UUID


class GetRoleResponse(ORMModel):
    role: str


class GetSigninUrlResponse(ORMModel):
    signin_url: str


class GetConveyorIdeUrlResponse(ORMModel):
    ide_url: str


class GetDatabricksWorkspaceUrlResponse(ORMModel):
    databricks_workspace_url: str


class GetSnowflakeUrlResponse(ORMModel):
    snowflake_url: str
