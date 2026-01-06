from uuid import UUID
from warnings import deprecated

from app.authorization.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class TechnicalAssetOutputPortAssociation(ORMModel):
    id: UUID
    output_port_id: UUID
    technical_asset_id: UUID
    status: DecisionStatus


@deprecated("TechnicalAssetOutputPortAssociation instead")
class DataOutputDatasetAssociation(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DecisionStatus

    def convert(self) -> TechnicalAssetOutputPortAssociation:
        return TechnicalAssetOutputPortAssociation(
            id=self.id,
            output_port_id=self.dataset_id,
            technical_asset_id=self.data_output_id,
            status=self.status,
        )
