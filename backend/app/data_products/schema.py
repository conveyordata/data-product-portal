from typing import Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.schema import DataProductType
from app.data_products.status import AbstractDataProductStatus
from app.shared.schema import ORMModel


class DataProduct(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: AbstractDataProductStatus
    type: DataProductType


class OutputPortEmbed(ORMModel):
    name: str
    description: str


class TechnicalAssetEmbed(ORMModel):
    name: str
    description: str


class DataProductEmbedModel(ORMModel):
    name: str
    description: Optional[str]
    output_ports: list[OutputPortEmbed] = Field(validation_alias="datasets")
    technical_assets: list[TechnicalAssetEmbed]
    about: Optional[str]

    @field_validator("technical_assets", mode="before")
    @classmethod
    def keep_exposed_technical_assets(cls, v):
        return [
            technical_asset
            for technical_asset in v
            if any(
                link.status == DecisionStatus.APPROVED
                for link in technical_asset.output_port_links
            )
        ]
