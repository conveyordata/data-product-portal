import pytest
from fastapi import HTTPException

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.authorization.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.authorization.roles.schema import Scope
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.groups.service import GroupService
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    GroupFactory,
    MachineUserFactory,
    RoleFactory,
    UserFactory,
)


class TestGroupService:
    def test_no_nested_groups(self, session):
        parent_group = GroupFactory()
        member_group = GroupFactory()
        service = GroupService(session)

        with pytest.raises(
            HTTPException, match="Only users and machine users can be group members."
        ):
            service.add_member(
                group_id=parent_group.id,
                member_identity_id=member_group.id,
            )

    def test_user_can_belong_to_group(self, session):
        group = GroupFactory()
        user = UserFactory()
        service = GroupService(session)

        service.add_member(group_id=group.id, member_identity_id=user.id)
        membership = service.get_membership(
            group_id=group.id, member_identity_id=user.id
        )
        assert membership.group_id == group.id
        assert membership.member_identity_id == user.id

    def test_machine_user_can_belong_to_group(self, session):
        group = GroupFactory()
        machine_user = MachineUserFactory()
        service = GroupService(session)

        service.add_member(group_id=group.id, member_identity_id=machine_user.id)
        membership = service.get_membership(
            group_id=group.id, member_identity_id=machine_user.id
        )
        assert membership.group_id == group.id
        assert membership.member_identity_id == machine_user.id

    def test_duplicate_membership_is_rejected(self, session):
        group = GroupFactory()
        user = UserFactory()
        service = GroupService(session)

        service.add_member(group_id=group.id, member_identity_id=user.id)
        with pytest.raises(
            HTTPException, match="The identity is already a member of this group."
        ):
            service.add_member(group_id=group.id, member_identity_id=user.id)

        assert len(service.list_memberships(group_id=group.id)) == 1

    def test_deleting_group_deletes_its_memberships(self, session):
        group = GroupFactory()
        group_id = group.id
        user1 = UserFactory()
        user2 = UserFactory()
        service = GroupService(session)

        service.add_member(group_id=group_id, member_identity_id=user1.id)
        service.add_member(group_id=group_id, member_identity_id=user2.id)

        service.delete_group(group_id=group_id)
        with pytest.raises(HTTPException):
            service.get_group(group_id=group_id)
        with pytest.raises(HTTPException):
            service.get_membership(group_id=group_id, member_identity_id=user1.id)
        with pytest.raises(HTTPException):
            service.get_membership(group_id=group_id, member_identity_id=user2.id)

        # Members themselves must remain.
        assert user1 in session
        assert user2 in session

    def test_deleting_group_deletes_its_role_assignments(self, session):
        group = GroupFactory()
        actor = UserFactory()
        data_product = DataProductFactory()
        data_product_role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])
        global_role = RoleFactory(scope=Scope.GLOBAL, permissions=[])
        service = GroupService(session)

        data_product_assignment = DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=data_product_role.id,
            requested_by_id=actor.id,
            decided_by_id=actor.id,
        )
        global_assignment = GlobalRoleAssignmentFactory(
            identity_id=group.id,
            role_id=global_role.id,
            requested_by_id=actor.id,
            decided_by_id=actor.id,
        )

        group_id = group.id
        data_product_assignment_id = data_product_assignment.id
        global_assignment_id = global_assignment.id

        service.delete_group(group_id=group_id)
        with pytest.raises(HTTPException):
            service.get_group(group_id=group_id)
        with pytest.raises(HTTPException):
            DataProductRoleAssignmentService(session).get_assignment(
                data_product_assignment_id
            )
        with pytest.raises(HTTPException):
            GlobalRoleAssignmentService(session).get_assignment(global_assignment_id)

    def test_is_group__identifies_group_identity(self, session):
        group = GroupFactory()
        user = UserFactory()
        service = GroupService(session)

        assert service.is_group(group.id)
        assert not service.is_group(user.id)

    def test_membership__immediately_adds_and_revokes_existing_group_access(
        self,
        authorizer: Authorization,
        session,
    ):
        group = GroupFactory()
        user = UserFactory()
        data_product = DataProductFactory()

        data_product_action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        global_action = AuthorizationAction.DATA_PRODUCT__DELETE

        data_product_role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[data_product_action],
        )
        global_role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[global_action],
        )

        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=data_product_role.id,
        )
        GlobalRoleAssignmentFactory(
            identity_id=group.id,
            role_id=global_role.id,
        )

        service = GroupService(session)
        service.add_member(
            group_id=group.id,
            member_identity_id=user.id,
        )

        assert authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=data_product_action,
        )
        assert authorizer.has_access(
            sub=str(user.id),
            dom="*",
            obj="*",
            act=global_action,
        )

        service.remove_member(
            group_id=group.id,
            member_identity_id=user.id,
        )

        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=data_product_action,
        )
        assert not authorizer.has_access(
            sub=str(user.id),
            dom="*",
            obj="*",
            act=global_action,
        )

    def test_data_product_membership_edges__immediately_updates_existing_members(
        self,
        authorizer: Authorization,
        session,
    ):
        group = GroupFactory()
        user = UserFactory()
        data_product = DataProductFactory()
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        service = GroupService(session)
        service.add_member(
            group_id=group.id,
            member_identity_id=user.id,
        )

        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[action],
        )
        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=role.id,
        )

        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=action,
        )

        service.add_data_product_membership_edges(
            group_id=group.id,
            data_product_id=data_product.id,
        )

        assert authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=action,
        )

        service.remove_data_product_membership_edges(
            group_id=group.id,
            data_product_id=data_product.id,
        )

        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=action,
        )
