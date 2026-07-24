from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class ApproveOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
    decision_note: Optional[str] = None


class DenyOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
    decision_note: str


class RevokeOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID


class RemoveOutputPortAsInputPortRequest(ORMModel):
    consuming_data_product_id: UUID
