from typing import Generic, TypeVar
from uuid import UUID

from pydantic import Field, SkipValidation, field_validator

from app.settings import settings
from app.shared.schema import ORMModel

BatchItem = TypeVar("BatchItem", bound=ORMModel)


class IdentityBatchCreateRequest(ORMModel, Generic[BatchItem]):
    """
    Generic way to represent a batch item, then defined in the specific router.
    This way the openapi spec will show a list of the required objects.

    The item needs to be validated in the router before any action; this allows
    for partial errors that doesn't interrupt the batch processing.
    """

    items: list[SkipValidation[BatchItem]] = Field(
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
