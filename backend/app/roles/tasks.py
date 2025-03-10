from dataclasses import dataclass

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.roles.schema import Role, Scope


@dataclass
class AuthRole:
    """Dataclass to pass values separate from the DB session."""

    id: str
    scope: Scope
    permissions: list[AuthorizationAction]

    @classmethod
    def from_role(cls, role: Role) -> "AuthRole":
        return AuthRole(id=str(role.id), scope=role.scope, permissions=role.permissions)


async def sync_role(role: AuthRole) -> None:
    authorizer = Authorization()
    await authorizer.sync_role_permissions(role_id=role.id, actions=role.permissions)


async def remove_role(role: AuthRole) -> None:
    authorizer = Authorization()
    await authorizer.remove_role_permissions(role_id=role.id)

    if role.scope == Scope.DATASET or role.scope == Scope.DATA_PRODUCT:
        await authorizer.clear_assignments_for_resource_role(role_id=role.id)
    elif role.scope == Scope.DOMAIN:
        await authorizer.clear_assignments_for_domain_role(role_id=role.id)
