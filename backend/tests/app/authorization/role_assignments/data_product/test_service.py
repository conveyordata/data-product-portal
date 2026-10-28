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
    GroupFactory,
    GroupMembershipFactory,
    MachineUserFactory,
    RoleFactory,
    UserFactory,
)
from tests.session_util import as_user


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
            data_product_id=data_product.id, identity_id=user.id, role_id=role.id
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
            identity_id=user.id,
            requested_by=user,
            requested_on=datetime.now(timezone.utc),
            decision=DecisionStatus.PENDING,
            data_product_id=DataProductFactory().id,
            role_id=role.id,
        )
        pending_old = DataProductRoleAssignmentFactory(
            identity_id=user.id,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            decision=DecisionStatus.PENDING,
            data_product_id=DataProductFactory().id,
            role_id=role.id,
        )
        approved_old = DataProductRoleAssignmentFactory(
            identity_id=user.id,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            decision=DecisionStatus.APPROVED,
            data_product_id=DataProductFactory().id,
            role_id=role.id,
        )
        with as_user(session, user.id):
            requests_old_inactive_hidden = RoleAssignmentService(
                session
            ).get_user_requests(user, True)
            requests_all = RoleAssignmentService(session).get_user_requests(user, False)
            assert len(requests_old_inactive_hidden) == 2
            assert len(requests_all) == 3
            requests_ids = [r.id for r in requests_old_inactive_hidden]
            assert pending_recent.id in requests_ids
            assert pending_old.id in requests_ids
            assert approved_old.id not in requests_ids

    def test_get_pending_data_product_role_assignments__includes_group_permissions(
        self,
        session,
    ):
        approver = UserFactory()
        requester = UserFactory()
        group = GroupFactory()
        data_product = DataProductFactory()

        GroupMembershipFactory(group=group, member=approver)
        approver_role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__APPROVE_USER_REQUEST],
        )
        requested_role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[],
        )
        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=approver_role.id,
            decision=DecisionStatus.APPROVED,
            requested_by=requester,
        )
        pending_assignment = DataProductRoleAssignmentFactory(
            identity_id=requester.id,
            data_product_id=data_product.id,
            role_id=requested_role.id,
            decision=DecisionStatus.PENDING,
            requested_by=requester,
        )

        with as_user(session, approver.id):
            pending_actions = RoleAssignmentService(
                session
            ).get_pending_data_product_role_assignments(approver)

        assert {assignment.id for assignment in pending_actions} == {
            pending_assignment.id
        }

    def test_users_with_authz_action__includes_users_from_assigned_groups(
        self,
        session,
    ):
        direct_user = UserFactory()
        group_member = UserFactory()
        unrelated_user = UserFactory()
        direct_machine_user = MachineUserFactory()
        machine_group_member = MachineUserFactory()
        group = GroupFactory()
        data_product = DataProductFactory()
        action = Action.DATA_PRODUCT__APPROVE_USER_REQUEST

        GroupMembershipFactory(group=group, member=group_member)
        GroupMembershipFactory(group=group, member=machine_group_member)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[action],
        )
        DataProductRoleAssignmentFactory(
            identity_id=direct_user.id,
            data_product_id=data_product.id,
            role_id=role.id,
        )
        DataProductRoleAssignmentFactory(
            identity_id=direct_machine_user.id,
            data_product_id=data_product.id,
            role_id=role.id,
        )
        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=role.id,
        )
        authorized_users = RoleAssignmentService(session).users_with_authz_action(
            data_product_id=data_product.id,
            action=action,
        )

        authorized_user_ids = {user.id for user in authorized_users}

        assert authorized_user_ids == {
            direct_user.id,
            group_member.id,
        }
        assert unrelated_user.id not in authorized_user_ids
        assert direct_machine_user.id not in authorized_user_ids
        assert machine_group_member.id not in authorized_user_ids
