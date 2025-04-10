from typing import cast

from casbin_async_sqlalchemy_adapter import CasbinRule
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.role_assignments.dataset.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.roles.service import RoleService
from app.users.schema import User


class AuthorizationService:
    def __init__(self, db: Session, authorizer: Authorization) -> None:
        self.db = db
        self.authorizer = authorizer

    async def reload_enforcer(self):
        self._clear_casbin_table()

        await self._sync_roles()
        await self._sync_product_assignments()
        await self._sync_dataset_assignments()
        await self._sync_global_assignments()

    def _clear_casbin_table(self):
        self.db.execute(delete(CasbinRule))

    async def _sync_roles(self):
        service = RoleService(self.db)
        roles = service.get_roles()

        for role in roles:
            await self.authorizer.sync_role_permissions(
                role_id=str(role.id), actions=role.permissions
            )

    async def _sync_product_assignments(self):
        service = DataProductRoleAssignmentService(self.db, cast(User, None))
        product_assignments = service.list_assignments(
            data_product_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in product_assignments:
            await self.authorizer.assign_resource_role(
                user_id=str(assignment.user_id),
                role_id=str(assignment.role_id),
                resource_id=str(assignment.data_product_id),
            )

    async def _sync_dataset_assignments(self):
        service = DatasetRoleAssignmentService(self.db, cast(User, None))
        dataset_assignments = service.list_assignments(
            dataset_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in dataset_assignments:
            await self.authorizer.assign_resource_role(
                user_id=str(assignment.user_id),
                role_id=str(assignment.role_id),
                resource_id=str(assignment.dataset_id),
            )

    async def _sync_global_assignments(self):
        service = GlobalRoleAssignmentService(self.db, cast(User, None))
        global_assignments = service.list_assignments(
            user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in global_assignments:
            if assignment.is_admin():
                await self.authorizer.assign_admin_role(user_id=str(assignment.user_id))
            else:
                await self.authorizer.assign_global_role(
                    user_id=str(assignment.user_id),
                    role_id=str(assignment.role_id),
                )
