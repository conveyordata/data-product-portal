from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import (
    DatasetSettingValue,
    OutputPortSettingValue,
)
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_products.output_port_technical_assets_link.schema import (
    DataOutputDatasetAssociation,
    TechnicalAssetOutputPortAssociation,
)
from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.schema import (
    DataProductDatasetAssociation,
)
from app.data_products.output_ports.schema import OutputPort
from app.data_products.output_ports.status import OutputPortStatus
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.schema import TechnicalAsset
from app.shared.schema import ORMModel


class DataProductLink(DataProductDatasetAssociation):
    justification: str
    data_product: DataProduct


@deprecated("Use TechnicalAsset instead")
class DatasetDataOutput(TechnicalAsset):
    # Nested schemas
    owner: DataProduct

    def convert(self):
        return TechnicalAsset(**self.model_dump(exclude={"owner"}))


class TechnicalAssetLink(TechnicalAssetOutputPortAssociation):
    technical_asset: TechnicalAsset


@deprecated("Use TechnicalAssetLink instead")
class DataOutputLink(DataOutputDatasetAssociation):
    data_output: DatasetDataOutput

    def convert(self):
        return TechnicalAssetLink(
            **self.model_dump(exclude={"data_output", "data_output_id", "dataset_id"}),
            technical_asset=self.data_output.convert(),
            technical_asset_id=self.data_output_id,
            output_port_id=self.dataset_id,
        )


class BaseOutputPortGet(ORMModel):
    id: UUID
    namespace: str
    name: str
    description: str
    status: OutputPortStatus
    usage: Optional[str]
    access_type: OutputPortAccessType
    data_product_id: UUID

    # Nested schemas
    tags: list[Tag]
    domain: Domain
    lifecycle: Optional[DataProductLifeCycle]
    data_product_settings: list[OutputPortSettingValue]
    technical_asset_links: list[TechnicalAssetLink]


@deprecated("Use BaseOutputPortGet instead")
class BaseDatasetGet(ORMModel):
    id: UUID
    namespace: str
    name: str
    description: str
    status: OutputPortStatus
    usage: Optional[str]
    access_type: OutputPortAccessType
    data_product_id: UUID

    # Nested schemas
    tags: list[Tag]
    domain: Domain
    lifecycle: Optional[DataProductLifeCycle]

    # There can only be one
    data_product_settings: list[DatasetSettingValue]
    data_output_links: list[DataOutputLink]


class GetOutputPortResponse(BaseOutputPortGet):
    about: Optional[str]

    rolled_up_tags: set[Tag]


@deprecated("Use GetOutputPortResponse instead")
class DatasetGet(BaseDatasetGet):
    about: Optional[str]

    # Nested schemas
    data_product_links: list[DataProductLink]
    rolled_up_tags: set[Tag]

    def convert(self):
        return GetOutputPortResponse(
            id=self.id,
            namespace=self.namespace,
            name=self.name,
            description=self.description,
            status=self.status,
            usage=self.usage,
            access_type=self.access_type,
            data_product_id=self.data_product_id,
            tags=self.tags,
            domain=self.domain,
            lifecycle=self.lifecycle,
            about=self.about,
            rolled_up_tags=self.rolled_up_tags,
            technical_asset_links=[dol.convert() for dol in self.data_output_links],
            data_product_settings=[s.convert() for s in self.data_product_settings],
        )


class OutputPortsGet(BaseOutputPortGet):
    data_product_count: int
    data_product_name: str
    quality_status: Optional[DataQualityStatus]


@deprecated("Use OutputPortsGet instead")
class DatasetsGet(BaseDatasetGet):
    data_product_count: int
    data_product_name: str
    quality_status: Optional[DataQualityStatus]


class GetDataProductOutputPortsResponse(ORMModel):
    output_ports: Sequence[OutputPort]


class CreateOutputPortResponse(ORMModel):
    id: UUID


class UpdateOutputPortResponse(ORMModel):
    id: UUID
