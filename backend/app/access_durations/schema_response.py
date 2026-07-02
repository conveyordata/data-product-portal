from uuid import UUID

from app.shared.schema import ORMModel


class AccessDuration(ORMModel):
    id: UUID
    abstract_data_product_type: str
    access_duration_type: str
    days: int | None
    is_default: bool
