from uuid import UUID
from warnings import deprecated

from pydantic import Field

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
    output_port_id: UUID = Field(validation_alias="dataset_id")
    technical_asset_id: UUID = Field(validation_alias="data_output_id")
    status: DecisionStatus
