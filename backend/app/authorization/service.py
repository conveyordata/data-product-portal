from typing import cast

from casbin import Enforcer
from casbin_sqlalchemy_adapter import Adapter, CasbinRule
from sqlalchemy import delete
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

    def reload_enforcer(self):
        self._clear_casbin_table()

        self._sync_roles()
        self._sync_product_assignments()
        self._sync_dataset_assignments()
        self._sync_global_assignments()

    @staticmethod
    def _clear_casbin_table() -> None:
        """Clears the database table used by casbin. Use with caution!
        This means the casbin table will be out of sync with the role assignments.
        """
        authorizer = Authorization()
        enforcer: Enforcer = authorizer._enforcer
        adapter: Adapter = enforcer.adapter

        with adapter._session_scope() as session:
            session.execute(delete(CasbinRule))

    def _sync_roles(self):
        service = RoleService(self.db)
        roles = service.get_roles()

        for role in roles:
            AuthRole(role).sync()

    def _sync_product_assignments(self):
        service = DataProductRoleAssignmentService(self.db, cast(User, None))
        product_assignments = service.list_assignments(
            data_product_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in product_assignments:
            DataProductAuthAssignment(assignment).add()

    def _sync_dataset_assignments(self):
        service = DatasetRoleAssignmentService(self.db, cast(User, None))
        dataset_assignments = service.list_assignments(
            dataset_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in dataset_assignments:
            DatasetAuthAssignment(assignment).add()

    def _sync_global_assignments(self):
        service = GlobalRoleAssignmentService(self.db, cast(User, None))
        global_assignments = service.list_assignments(
            user_id=None, decision=DecisionStatus.APPROVED
        )

        for assignment in global_assignments:
            GlobalAuthAssignment(assignment).add()
