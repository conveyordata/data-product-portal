from casbin_sqlalchemy_adapter import CasbinRule
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.auth import (
    DataProductAuthAssignment,
)
from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.auth import GlobalAuthAssignment
from app.authorization.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.authorization.role_assignments.output_port.auth import DatasetAuthAssignment
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.authorization.roles.auth import AuthRole
from app.authorization.roles.service import RoleService
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.core.logging import logger

DATA_PRODUCT_READER_ROLE = "/role/data-product-reader"


class AuthorizationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.authorizer = Authorization()

    def reload_enforcer(self) -> None:
        self.authorizer.pause_enforcer_for_reload()

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

        self._sync_data_product_reader_role()
        logger.info("Synced data product reader role permissions")

        self.authorizer.start_enforcer_after_reload()

        logger.info(
            "Authorization reload done - the casbin table"
            f" now contains {self._casbin_row_count(self.db)} rows"
        )

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

    def _sync_data_product_reader_role(self):
        from app.data_products.service import DataProductService

        self.authorizer.sync_role_permissions(
            role_id=DATA_PRODUCT_READER_ROLE,
            actions=[AuthorizationAction.HIDDEN_DATA_PRODUCT__READ],
        )
        DataProductService(self.db).sync_discoverable_data_products()
