from typing import Optional
from uuid import UUID

from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.shared.schema import ORMModel


class Dataset(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: DatasetStatus
    access_type: DatasetAccessType
    data_product_id: Optional[UUID]
