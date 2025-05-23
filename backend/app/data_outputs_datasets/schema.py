from uuid import UUID

from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class DataOutputDatasetAssociation(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DecisionStatus
