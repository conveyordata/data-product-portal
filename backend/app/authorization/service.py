from typing import cast

from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.role_assignments.data_product.auth import DataProductAuthAssignment
from app.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.role_assignments.dataset.auth import DatasetAuthAssignment
from app.role_assignments.dataset.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.auth import GlobalAuthAssignment
from app.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.roles.auth import AuthRole
from app.roles.service import RoleService
from app.users.schema import User


class AuthorizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.authorizer = Authorization()

    async def reload_enforcer(self):
        await self._clear_casbin_table()

        await self._sync_roles()
        await self._sync_product_assignments()
        await self._sync_dataset_assignments()
        await self._sync_global_assignments()

    async def _clear_casbin_table(self):
        authorizer = Authorization()
        await authorizer.clear_adapter()

    async def _sync_roles(self):
        service = RoleService(self.db)
        roles = service.get_roles()

        for role in roles:
            await AuthRole(role).sync()

    async def _sync_product_assignments(self):
        service = DataProductRoleAssignmentService(self.db, cast(User, None))
        product_assignments = service.list_assignments(
            data_product_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in product_assignments:
            await DataProductAuthAssignment(assignment).add()

    async def _sync_dataset_assignments(self):
        service = DatasetRoleAssignmentService(self.db, cast(User, None))
        dataset_assignments = service.list_assignments(
            dataset_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in dataset_assignments:
            await DatasetAuthAssignment(assignment).add()

    async def _sync_global_assignments(self):
        service = GlobalRoleAssignmentService(self.db, cast(User, None))
        global_assignments = service.list_assignments(
            user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in global_assignments:
            await GlobalAuthAssignment(assignment).add()
