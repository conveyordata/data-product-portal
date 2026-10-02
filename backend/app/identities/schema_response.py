from typing import Any
from uuid import UUID

from app.shared.schema import ORMModel


class IdentityBatchCreateError(ORMModel):
    item: Any
    errors: list[str]


class IdentityBatchCreateResponse(ORMModel):
    ids: list[UUID]
    errors: list[IdentityBatchCreateError]