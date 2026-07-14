from datetime import datetime, timedelta, timezone

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)


class TestDataProductRoleAssignmentsService:
    def test_user_has_permission(self, session):
        service = RoleAssignmentService(db=session)
        data_product = DataProductFactory()
        action = Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS

        authorized_users = service.users_with_authz_action(
            data_product_id=data_product.id,
            action=action,
        )
        assert len(authorized_users) == 0

        user = UserFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[action])
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id, user_id=user.id, role_id=role.id
        )

        authorized_users = service.users_with_authz_action(
            data_product_id=data_product.id,
            action=action,
        )
        assert user.id in (auth_user.id for auth_user in authorized_users)

    def test_get_user_requests(self, session):
        user = UserFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        pending_recent = DataProductRoleAssignmentFactory(
            user_id=user.id,
            requested_by=user,
            requested_on=datetime.now(timezone.utc),
            decision=DecisionStatus.PENDING,
            data_product_id=DataProductFactory().id,
            role_id=role.id,
        )
        pending_old = DataProductRoleAssignmentFactory(
            user_id=user.id,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            decision=DecisionStatus.PENDING,
            data_product_id=DataProductFactory().id,
            role_id=role.id,
        )
        approved_old = DataProductRoleAssignmentFactory(
            user_id=user.id,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            decision=DecisionStatus.APPROVED,
            data_product_id=DataProductFactory().id,
            role_id=role.id,
        )
        requests_old_inactive_hidden = RoleAssignmentService(session).get_user_requests(
            user, True
        )
        requests_all = RoleAssignmentService(session).get_user_requests(user, False)
        assert len(requests_old_inactive_hidden) == 2
        assert len(requests_all) == 3
        requests_ids = [r.id for r in requests_old_inactive_hidden]
        assert pending_recent.id in requests_ids
        assert pending_old.id in requests_ids
        assert approved_old.id not in requests_ids
