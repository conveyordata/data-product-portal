from dataclasses import dataclass

from app.core.authz import Action, Authorization
from app.roles.schema import Role, Scope


@dataclass
class _AuthRole:
    """Dataclass to pass values separate from the DB session."""

    id: str
    scope: Scope
    permissions: list[Action]


class AuthRole(_AuthRole):

    def __init__(self, role: Role):
        super().__init__(
            id=str(role.id), scope=role.scope, permissions=role.permissions
        )

    async def sync(self) -> None:
        authorizer = Authorization()
        await authorizer.sync_role_permissions(
            role_id=self.id, actions=self.permissions
        )

    async def remove(self) -> None:
        authorizer = Authorization()
        await authorizer.remove_role_permissions(role_id=self.id)

        if self.scope == Scope.DATASET or self.scope == Scope.DATA_PRODUCT:
            await authorizer.clear_assignments_for_resource_role(role_id=self.id)
        elif self.scope == Scope.DOMAIN:
            await authorizer.clear_assignments_for_domain_role(role_id=self.id)
