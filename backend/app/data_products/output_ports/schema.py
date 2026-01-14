from uuid import UUID
from warnings import deprecated

from pydantic import Field, field_validator

from app.configuration.tags.schema import Tag
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.status import OutputPortStatus
from app.shared.schema import ORMModel


class OutputPort(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: OutputPortStatus
    access_type: OutputPortAccessType
    data_product_id: UUID
    tags: list[Tag]


@deprecated("use OutputPort instead")
class Dataset(OutputPort):
    def convert(self) -> OutputPort:
        return OutputPort(**self.model_dump())


class DataProductEmbed(ORMModel):
    name: str
    description: str


class TechnicalAssetEmbed(ORMModel):
    name: str
    description: str


class DatasetEmbedModel(ORMModel):
    name: str
    namespace: str
    description: str
    data_product: DataProductEmbed
    technical_assets: list[TechnicalAssetEmbed] = Field(
        validation_alias="data_output_links"
    )

    @field_validator("technical_assets", mode="before")
    @classmethod
    def map_technical_assets(cls, v):
        return [link.data_output for link in v]
