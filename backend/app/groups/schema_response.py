from typing import Sequence
from uuid import UUID

from app.groups.schema import Group
from app.shared.schema import ORMModel


class GroupGet(Group):
    pass


class GroupsGetResponse(ORMModel):
    groups: Sequence[GroupGet]


class GroupCreateResponse(ORMModel):
    id: UUID


class GroupUpdateResponse(ORMModel):
    id: UUID