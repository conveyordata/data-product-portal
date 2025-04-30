from uuid import UUID

from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.shared.schema import ORMModel


class DatasetBasic(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: DatasetStatus
    access_type: DatasetAccessType
