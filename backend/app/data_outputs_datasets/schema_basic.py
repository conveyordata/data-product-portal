from uuid import UUID

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.shared.schema import ORMModel


class DataOutputDatasetAssociationBasic(ORMModel):
    id: UUID
    dataset_id: UUID
    data_output_id: UUID
    status: DataOutputDatasetLinkStatus
