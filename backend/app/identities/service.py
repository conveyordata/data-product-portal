from app.groups.model import Group
from app.identities.model import Identity
from app.machine_users.model import MachineUser
from app.users.model import User


def get_identity_display_name(identity: Identity) -> str:
    if isinstance(identity, User):
        return f"{identity.first_name} {identity.last_name}"

    if isinstance(identity, (Group, MachineUser)):
        return identity.display_name

    raise ValueError(f"Unsupported identity type: {identity.type}")
