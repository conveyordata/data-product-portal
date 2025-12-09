from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import DataProductSettingValue
from app.configuration.data_product_types.schema import DataProductType
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_outputs.schema_response import BaseDataOutputGet, BaseTechnicalAssetGet
from app.data_outputs_datasets.schema_response import (
    BaseDataOutputDatasetAssociationGet,
    BaseTechnicalAssetOutputPortAssociationGet,
)
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import (
    DataProductDatasetAssociation,
    DataProductOutputPortAssociation,
)
from app.datasets.schema import Dataset, OutputPort
from app.shared.schema import ORMModel


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    status: DataProductStatus

    # Nested schemas
    tags: list[Tag]
    usage: Optional[str]
    domain: Domain
    type: DataProductType
    lifecycle: Optional[DataProductLifeCycle]
    data_product_settings: list[DataProductSettingValue]


class TechnicalAssetLinks(BaseTechnicalAssetGet):
    # Nested schemas
    output_port_links: list[BaseTechnicalAssetOutputPortAssociationGet]


@deprecated("Use TechnicalAssetLinks instead")
class DataOutputLinks(BaseDataOutputGet):
    # Nested schemas
    dataset_links: list[BaseDataOutputDatasetAssociationGet]

    def convert(self) -> TechnicalAssetLinks:
        base = self.model_dump(exclude={"dataset_links"})
        return TechnicalAssetLinks(
            **base, output_port_links=[dl.convert() for dl in self.dataset_links]
        )


@deprecated("Use InputPort instead")
class DatasetLinks(DataProductDatasetAssociation):
    # Nested schemas
    dataset: Dataset

    def convert(self):
        base = self.model_dump(exclude={"dataset", "dataset_id"})
        return InputPort(
            **base,
            output_port_id=self.dataset_id,
            input_port=self.dataset.convert(),
        )


class InputPort(DataProductOutputPortAssociation):
    input_port: OutputPort


@deprecated("Use GetDataProductResponse instead")
class DataProductGet(BaseDataProductGet):
    about: Optional[str]

    # Nested schemas
    dataset_links: list[DatasetLinks]
    data_outputs: list[DataOutputLinks]
    datasets: list[Dataset]
    rolled_up_tags: set[Tag]


class GetDataProductResponse(BaseDataProductGet):
    about: Optional[str]

    # Nested schemas
    input_ports: list[InputPort]
    technical_assets: list[TechnicalAssetLinks]
    output_ports: list[OutputPort]
    rolled_up_tags: set[Tag]


class GetDataProductsResponseItem(BaseDataProductGet):
    user_count: int
    output_port_count: int
    technical_asset_count: int


@deprecated("Use GetDataProductsResponseItem instead")
class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int

    def convert(self) -> GetDataProductsResponseItem:
        base = self.model_dump(exclude={"dataset_count", "data_outputs_count"})
        return GetDataProductsResponseItem(
            **base,
            output_port_count=self.dataset_count,
            technical_asset_count=self.data_outputs_count,
        )


@deprecated("Use LinkInputPortsToDataProductPost instead")
class LinkDatasetsToDataProductPost(ORMModel):
    dataset_links: list[UUID]


class LinkInputPortsToDataProductPost(ORMModel):
    input_port_links: list[UUID]


class GetDataProductsResponse(ORMModel):
    data_products: Sequence[GetDataProductsResponseItem]


class CreateDataProductResponse(ORMModel):
    id: UUID


class UpdateDataProductResponse(ORMModel):
    id: UUID


class CreateTechnicalAssetResponse(ORMModel):
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
