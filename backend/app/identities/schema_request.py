from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from app.settings import settings
from app.shared.schema import ORMModel


class IdentityBatchCreateRequest(ORMModel):
    items: list[Any] = Field(
        min_length=1,
        max_length=settings.MAX_ITEMS_PER_BATCH_REQUEST,
    )


class IdentityBatchDeleteRequest(ORMModel):
    ids: list[UUID] = Field(
        min_length=1,
        max_length=settings.MAX_ITEMS_PER_BATCH_REQUEST,
    )

    @field_validator("ids")
    @classmethod
    def reject_duplicate_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("Identity IDs must be unique.")
        return value
