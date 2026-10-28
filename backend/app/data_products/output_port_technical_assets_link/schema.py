from uuid import UUID
from warnings import deprecated

from pydantic import AliasChoices, Field

from app.authorization.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


@deprecated("TechnicalAssetOutputPortAssociation instead")
class DataOutputDatasetAssociation(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DecisionStatus


class TechnicalAssetOutputPortAssociation(ORMModel):
    id: UUID
    output_port_id: UUID = Field(
        validation_alias=AliasChoices("output_port_id", "dataset_id")
    )
    technical_asset_id: UUID = Field(
        validation_alias=AliasChoices("technical_asset_id", "data_output_id")
    )
    status: DecisionStatus
