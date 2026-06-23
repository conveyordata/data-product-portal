from datetime import datetime
from typing import Optional
from uuid import UUID
from warnings import deprecated

from pydantic import Field

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.schema import OutputPort
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.schema import (
    TechnicalAsset as TechnicalAssetBaseSchema,
)
from app.shared.schema import ORMModel
from app.users.schema import User


class OwnedTechnicalAsset(TechnicalAssetBaseSchema):
    owner: DataProduct


@deprecated("Use OwnedTechnicalAsset instead")
class DataOutput(TechnicalAssetBaseSchema):
    # Nested schemas
    owner: DataProduct

    def convert(self) -> OwnedTechnicalAsset:
        return OwnedTechnicalAsset(**self.model_dump())


class BaseTechnicalAssetOutputPortAssociationGet(ORMModel):
    id: UUID
    output_port_id: UUID = Field(validation_alias="dataset_id")
    output_port: OutputPort = Field(validation_alias="dataset")
    technical_asset_id: UUID = Field(validation_alias="data_output_id")
    technical_asset: OwnedTechnicalAsset = Field(validation_alias="data_output")
    status: DecisionStatus
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]

    # Nested schemas
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


class TechnicalAssetOutputPortAssociationsGet(
    BaseTechnicalAssetOutputPortAssociationGet
):
    pass


class LinkTechnicalAssetsToOutputPortResponse(ORMModel):
    link_id: UUID
