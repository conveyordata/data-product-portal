from typing import Optional, Sequence
from uuid import UUID

from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import OutputPortSettingValue
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_outputs.schema import DataOutput as DataOutputBaseSchema
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_products.schema import DataProduct
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.enums import OutputPortAccessType
from app.datasets.status import OutputPortStatus
from app.shared.schema import ORMModel


class DataProductLink(DataProductDatasetAssociation):
    justification: str
    data_product: DataProduct


class DataOutput(DataOutputBaseSchema):
    # Nested schemas
    owner: DataProduct


class DataOutputLink(DataOutputDatasetAssociation):
    data_output: DataOutput


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
    data_product_settings: list[OutputPortSettingValue]
    data_output_links: list[DataOutputLink]


class DatasetGet(BaseDatasetGet):
    about: Optional[str]

    # Nested schemas
    data_product_links: list[DataProductLink]
    rolled_up_tags: set[Tag]


class DatasetsGet(BaseDatasetGet):
    data_product_count: int
    data_product_name: str


class DatasetsSearch(DatasetsGet):
    rank: float


class DatasetEmbeddingResult(ORMModel):
    id: UUID
    distance: float


class DataOutputEmbed(ORMModel):
    name: str
    namespace: str
    description: str


class DataOutputLinkEmbed(ORMModel):
    data_output: DataOutputEmbed


class DataProductEmbed(ORMModel):
    name: str
    description: str


class DatasetEmbed(ORMModel):
    id: UUID
    name: str
    description: str
    about: Optional[str]
    status: OutputPortStatus
    domain: Domain
    data_product: DataProductEmbed
    data_output_links: list[DataOutputLinkEmbed]


class DatasetsAIGet(DatasetsGet):
    pass


class DatasetsAISearch(DatasetsSearch):
    reason: Optional[str]


class DatasetAIReason(ORMModel):
    reason: str


class DatasetEmbedReturn(ORMModel):
    id: UUID
    rank: float
    reason: str
    name: str
    description: str
    about: Optional[str]
    status: OutputPortStatus

    class DataProductEmbed(ORMModel):
        name: str
        description: str

    data_product: DataProductEmbed

    class TechnicalAssetsEmbed(ORMModel):
        name: str
        description: str


class DatasetsAISearchResult(ORMModel):
    datasets: Sequence[DatasetsAISearch]
    reasoning: str
