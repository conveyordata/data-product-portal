from datetime import datetime
from typing import Optional
from uuid import UUID
from warnings import deprecated

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.schema import Dataset
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.schema import DataOutput as DataOutputBaseSchema
from app.data_products.technical_assets.schema import (
    TechnicalAsset as TechnicalAssetBaseSchema,
)
from app.shared.schema import ORMModel
from app.users.schema import User


class TechnicalAsset(TechnicalAssetBaseSchema):
    owner: DataProduct


@deprecated("Use TechnicalAsset instead")
class DataOutput(DataOutputBaseSchema):
    # Nested schemas
    owner: DataProduct

    def convert(self) -> TechnicalAsset:
        return TechnicalAsset(**self.model_dump())


class BaseTechnicalAssetOutputPortAssociationGet(ORMModel):
    id: UUID
    output_port_id: UUID
    technical_asset_id: UUID
    status: DecisionStatus
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]

    # Nested schemas
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]


class BaseDataOutputDatasetAssociationGet(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DecisionStatus
    requested_on: datetime
    denied_on: Optional[datetime]
    approved_on: Optional[datetime]

    # Nested schemas
    dataset: Dataset
    data_output: DataOutput
    requested_by: User
    denied_by: Optional[User]
    approved_by: Optional[User]

    def convert(self) -> BaseTechnicalAssetOutputPortAssociationGet:
        base = self.model_dump(
            exclude={"dataset_id", "data_output_id", "dataset", "data_output"}
        )
        return BaseTechnicalAssetOutputPortAssociationGet(
            **base,
            output_port_id=self.dataset_id,
            technical_asset_id=self.data_output_id,
        )


class DataOutputDatasetAssociationGet(BaseDataOutputDatasetAssociationGet):
    pass


class DataOutputDatasetAssociationsGet(BaseDataOutputDatasetAssociationGet):
    pass


class TechnicalAssetOutputPortAssociationsGet(
    BaseTechnicalAssetOutputPortAssociationGet
):
    pass


class LinkTechnicalAssetsToOutputPortResponse(ORMModel):
    link_id: UUID
