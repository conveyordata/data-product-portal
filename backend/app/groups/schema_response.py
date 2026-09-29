from typing import Sequence
from uuid import UUID

from app.groups.schema import Group
from app.identities.type import IdentityType
from app.shared.schema import ORMModel


class GroupGet(Group):
    pass


class GroupsGetResponse(ORMModel):
    groups: Sequence[GroupGet]


class GroupCreateResponse(ORMModel):
    id: UUID


class GroupUpdateResponse(ORMModel):
    id: UUID

class GroupMemberIdentityGet(ORMModel):
    id: UUID
    type: IdentityType
    external_id: str


class GroupMembershipGet(ORMModel):
    group_id: UUID
    member_identity_id: UUID
    member: GroupMemberIdentityGet


class GroupMembershipsGetResponse(ORMModel):
    members: Sequence[GroupMembershipGet]