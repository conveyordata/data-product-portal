from dataclasses import dataclass

from app.authorization.roles.schema import Prototype, Role, Scope
from app.core.authz import Action, CasbinPolicies


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

    def sync(self) -> bool:
        authorizer = CasbinPolicies()
        if self.prototype == Prototype.EVERYONE:
            return authorizer.sync_everyone_role_permissions(actions=self.permissions)
        else:
            return authorizer.sync_role_permissions(
                role_id=self.id, actions=self.permissions
            )

    def remove(self) -> None:
        authorizer = CasbinPolicies()
        authorizer.remove_role_permissions(role_id=self.id)

        if self.scope == Scope.DATASET or self.scope == Scope.DATA_PRODUCT:
            authorizer.clear_assignments_for_resource_role(role_id=self.id)
        elif self.scope == Scope.DOMAIN:
            authorizer.clear_assignments_for_domain_role(role_id=self.id)
        elif self.scope == Scope.GLOBAL:
            authorizer.clear_assignments_for_global_role(role_id=self.id)
