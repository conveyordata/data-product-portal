from uuid import UUID

from app.data_outputs.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class DataOutputGet(ORMModel):
    id: UUID
    name: str
    external_id: str
    owner_id: UUID
    configuration_type: DataOutputTypes
