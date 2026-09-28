from collections.abc import Sequence
from uuid import UUID

from app.machine_users.schema import MachineUser
from app.shared.schema import ORMModel


class MachineUserGet(MachineUser):
    pass


class MachineUsersGetResponse(ORMModel):
    machine_users: Sequence[MachineUserGet]


class MachineUserCreateResponse(ORMModel):
    id: UUID


class MachineUserUpdateResponse(ORMModel):
    id: UUID