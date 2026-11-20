from typing import Annotated, Literal

from pydantic import Field

from app.groups.schema import Group
from app.identities.type import IdentityType
from app.machine_users.schema import MachineUser
from app.users.schema import User


class UserIdentity(User):
    type: Literal[IdentityType.USER]


class GroupIdentity(Group):
    type: Literal[IdentityType.GROUP]


class MachineUserIdentity(MachineUser):
    type: Literal[IdentityType.MACHINE_USER]


# Because the frontend cannot identify the type of the Identity,
# this is introduced to avoid setting a "type" param on every type response schema.
type Identity = Annotated[
    UserIdentity | GroupIdentity | MachineUserIdentity,
    Field(discriminator="type"),
]
