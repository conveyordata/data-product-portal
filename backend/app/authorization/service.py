from casbin import Enforcer
from casbin_sqlalchemy_adapter import Adapter, CasbinRule
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.core.logging import logger
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


class AuthorizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.authorizer = Authorization()

    def reload_enforcer(self) -> None:
        removed = self._clear_casbin_table()
        logger.info(f"Removed {removed} rows from the casbin table")

        changed_roles, total_roles = self._sync_roles()
        logger.info(f"Synced {changed_roles}/{total_roles} roles to the casbin table")

        changed_product_a, total_product_a = self._sync_product_assignments()
        logger.info(
            f"Synced {changed_product_a}/{total_product_a}"
            " product assignments to the casbin table"
        )

        changed_dataset_a, total_dataset_a = self._sync_dataset_assignments()
        logger.info(
            f"Synced {changed_dataset_a}/{total_dataset_a}"
            " dataset assignments to the casbin table"
        )

        changed_global_a, total_global_a = self._sync_global_assignments()
        logger.info(
            f"Synced {changed_global_a}/{total_global_a}"
            " global assignments to the casbin table"
        )

        logger.info(
            "Authorization reload done - the casbin table"
            f" now contains {self._casbin_row_count(self.db)} rows"
        )

    @classmethod
    def _clear_casbin_table(cls) -> int:
        """Clears the database table used by casbin. Use with caution!
        This means the casbin table will be out of sync with the role assignments.
        """
        authorizer = Authorization()
        enforcer: Enforcer = authorizer._enforcer
        adapter: Adapter = enforcer.adapter

        enforcer.clear_policy()
        with adapter._session_scope() as session:
            count = cls._casbin_row_count(session)
            session.execute(delete(CasbinRule))
        return count

    @staticmethod
    def _casbin_row_count(session: Session) -> int:
        return session.scalar(select(func.count()).select_from(CasbinRule))

    def _sync_roles(self) -> tuple[int, int]:
        service = RoleService(self.db)
        roles = service.get_roles()

        changes = 0
        for role in roles:
            if AuthRole(role).sync():
                changes += 1
        return changes, len(roles)

    def _sync_product_assignments(self) -> tuple[int, int]:
        service = DataProductRoleAssignmentService(self.db)
        product_assignments = service.list_assignments(
            data_product_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        changes = 0
        for assignment in product_assignments:
            if DataProductAuthAssignment(assignment).add():
                changes += 1
        return changes, len(product_assignments)

    def _sync_dataset_assignments(self) -> tuple[int, int]:
        service = DatasetRoleAssignmentService(self.db)
        dataset_assignments = service.list_assignments(
            dataset_id=None, user_id=None, decision=DecisionStatus.APPROVED
        )

        changes = 0
        for assignment in dataset_assignments:
            if DatasetAuthAssignment(assignment).add():
                changes += 1
        return changes, len(dataset_assignments)

    def _sync_global_assignments(self) -> tuple[int, int]:
        service = GlobalRoleAssignmentService(self.db)
        global_assignments = service.list_assignments(
            user_id=None, decision=DecisionStatus.APPROVED
        )

        changes = 0
        for assignment in global_assignments:
            if GlobalAuthAssignment(assignment).add():
                changes += 1
        return changes, len(global_assignments)
