from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.settings import settings
from app.shared.schema import ORMModel, NonEmptyStr


class GroupCreate(ORMModel):
    external_id: NonEmptyStr
    display_name: NonEmptyStr


class GroupUpdate(ORMModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    display_name: NonEmptyStr


class GroupMembersRequest(ORMModel):
    member_identity_ids: list[UUID] = Field(
        min_length=1, max_length=settings.MAX_ITEMS_PER_BATCH_REQUEST
    )

    @field_validator("member_identity_ids")
    @classmethod
    def reject_duplicate_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("Member identity IDs must be unique.")
        return value


class GroupMembersAdd(GroupMembersRequest):
    pass


class GroupMembersRemove(GroupMembersRequest):
    pass


class GroupMembersReplace(GroupMembersRequest):
    pass
