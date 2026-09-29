from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from app.shared.schema import ORMModel


class GroupCreate(ORMModel):
    external_id: str
    display_name: str


class GroupUpdate(ORMModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")
    display_name: str


class GroupMembersRequest(ORMModel):
    member_identity_ids: list[UUID]

    @field_validator("member_identity_ids")
    @classmethod
    def reject_duplicate_ids(cls, value: list[UUID]) -> list[UUID]:
        if len(value) != len(set(value)):
            raise ValueError("Member identity IDs must be unique.")
        return value


class GroupMembersAdd(GroupMembersRequest):
    member_identity_ids: list[UUID] = Field(min_length=1)


class GroupMembersRemove(GroupMembersRequest):
    member_identity_ids: list[UUID] = Field(min_length=1)


class GroupMembersReplace(GroupMembersRequest):
    member_identity_ids: list[UUID] = Field(min_length=1)
