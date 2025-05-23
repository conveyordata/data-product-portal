from dataclasses import dataclass

from app.core.authz import Action, Authorization
from app.roles.schema import Prototype, Role, Scope


@dataclass
class _AuthRole:
    """Dataclass to pass values separate from the DB session."""

    id: str
    scope: Scope
    prototype: Prototype
    permissions: list[Action]


class AuthRole(_AuthRole):

    def __init__(self, role: Role):
        super().__init__(
            id=str(role.id),
            scope=role.scope,
            prototype=role.prototype,
            permissions=role.permissions,
        )

    def sync(self) -> None:
        authorizer = Authorization()
        if self.prototype == Prototype.EVERYONE:
            authorizer.sync_everyone_role_permissions(actions=self.permissions)
        else:
            authorizer.sync_role_permissions(role_id=self.id, actions=self.permissions)

    def remove(self) -> None:
        authorizer = Authorization()
        authorizer.remove_role_permissions(role_id=self.id)

        if self.scope == Scope.DATASET or self.scope == Scope.DATA_PRODUCT:
            authorizer.clear_assignments_for_resource_role(role_id=self.id)
        elif self.scope == Scope.DOMAIN:
            authorizer.clear_assignments_for_domain_role(role_id=self.id)
