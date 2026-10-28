from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.authorization.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.authorization.roles.schema import Scope
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.groups.model import Group
from app.groups.schema_request import GroupCreate, GroupUpdate
from app.groups.service import GroupService
from tests import engine
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    MachineUserFactory,
    RoleFactory,
    UserFactory,
)
from tests.groups_util import group_has_member


class TestGroupService:
    def test_no_nested_groups(self, session):
        parent_group = GroupFactory()
        member_group = GroupFactory()
        service = GroupService(session)

        with pytest.raises(HTTPException) as exc_info:
            service.add_members(
                group_id=parent_group.id,
                member_identity_ids=[member_group.id],
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == (
            "All member identities must exist and be users or machine users."
        )

    def test_user_can_belong_to_group(self, session):
        group = GroupFactory()
        user = UserFactory()
        service = GroupService(session)

        service.add_members(group_id=group.id, member_identity_ids=[user.id])
        assert group_has_member(session, group_id=group.id, member_identity_id=user.id)

    def test_machine_user_can_belong_to_group(self, session):
        group = GroupFactory()
        machine_user = MachineUserFactory()
        service = GroupService(session)

        service.add_members(group_id=group.id, member_identity_ids=[machine_user.id])
        assert group_has_member(
            session, group_id=group.id, member_identity_id=machine_user.id
        )

    def test_duplicate_membership_is_ignored(self, session):
        group = GroupFactory()
        user = UserFactory()
        service = GroupService(session)

        service.add_members(
            group_id=group.id,
            member_identity_ids=[user.id],
        )
        service.add_members(
            group_id=group.id,
            member_identity_ids=[user.id],
        )

        memberships = service.list_memberships(group_id=group.id)

        assert len(memberships) == 1
        assert memberships[0].group_id == group.id
        assert memberships[0].member_identity_id == user.id

    def test_deleting_group_deletes_its_memberships(self, session):
        group = GroupFactory()
        group_id = group.id
        user1 = UserFactory()
        user2 = UserFactory()
        service = GroupService(session)

        service.add_members(group_id=group_id, member_identity_ids=[user1.id])
        service.add_members(group_id=group_id, member_identity_ids=[user2.id])

        service.delete_group(group_id=group_id)
        with pytest.raises(HTTPException):
            service.get_group(group_id=group_id)
        assert not group_has_member(
            session, group_id=group_id, member_identity_id=user1.id
        )
        assert not group_has_member(
            session, group_id=group_id, member_identity_id=user2.id
        )

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
        service.add_members(
            group_id=group.id,
            member_identity_ids=[user.id],
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

        service.remove_members(
            group_id=group.id,
            member_identity_ids=[user.id],
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

    def test_add_members__existing_member_immediately_inherits_new_group_data_product_role(
        self,
        authorizer: Authorization,
        session,
    ):
        group = GroupFactory()
        user = UserFactory()
        data_product = DataProductFactory()
        other_data_product = DataProductFactory()
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        service = GroupService(session)
        service.add_members(group_id=group.id, member_identity_ids=[user.id])
        assert authorizer.has_resource_role(
            user_id=user.id,
            role_id=group.id,
            resource_id="*",
        )
        assert not authorizer.has_resource_role(
            user_id=user.id,
            role_id=group.id,
            resource_id=data_product.id,
        )
        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=action,
        )

        role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[action])
        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=role.id,
        )
        assert authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=action,
        )
        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(other_data_product.domain_id),
            obj=str(other_data_product.id),
            act=action,
        )

        authorizer.revoke_resource_role(
            user_id=group.id,
            role_id=role.id,
            resource_id=data_product.id,
        )
        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=action,
        )
        # The reusable membership edge remains.
        assert authorizer.has_resource_role(
            user_id=user.id,
            role_id=group.id,
            resource_id="*",
        )

    def test_delete_group_deleting_group_revokes_inherited_access(
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
        service.add_members(
            group_id=group.id,
            member_identity_ids=[user.id],
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

        service.delete_group(group_id=group.id)
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
        assert not authorizer.has_resource_role(
            user_id=user.id,
            role_id=group.id,
            resource_id="*",
        )
        assert not authorizer.has_global_role(
            user_id=user.id,
            role_id=group.id,
        )

    def test_get_groups__returns_groups_ordered_by_display_name(self, session):
        second = GroupFactory(display_name="Beta", external_id="beta")
        first = GroupFactory(display_name="Alpha", external_id="alpha")

        groups = GroupService(session).get_groups()

        assert [group.id for group in groups] == [first.id, second.id]

    def test_get_group__returns_group(self, session):
        group = GroupFactory()

        result = GroupService(session).get_group(group.id)

        assert result.id == group.id
        assert result.external_id == group.external_id
        assert result.display_name == group.display_name

    def test_get_group__unknown_group_raises_not_found(self, session):
        service = GroupService(session)

        with pytest.raises(HTTPException) as exc_info:
            service.get_group(uuid4())

        assert exc_info.value.status_code == 404

    def test_create_group__creates_group(self, session):
        service = GroupService(session)

        result = service.create_group(
            GroupCreate(
                external_id="engineering",
                display_name="Engineering",
            )
        )

        group = service.get_group(result.id)
        assert group.external_id == "engineering"
        assert group.display_name == "Engineering"

    def test_create_group__rejects_duplicate_external_id(self, session):
        GroupFactory(external_id="engineering")
        service = GroupService(session)

        with pytest.raises(HTTPException) as exc_info:
            service.create_group(
                GroupCreate(
                    external_id="engineering",
                    display_name="Another Engineering Group",
                )
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "A group with this external ID already exists."

    def test_update_group__replaces_mutable_fields(self, session):
        group = GroupFactory(
            external_id="old-external-id",
            display_name="Old name",
        )
        service = GroupService(session)

        result = service.update_group(
            group.id,
            GroupUpdate(display_name="New name"),
        )

        session.refresh(group)
        assert result.id == group.id
        assert group.display_name == "New name"

    def test_update_group__unknown_group_raises_not_found(self, session):
        service = GroupService(session)

        with pytest.raises(HTTPException) as exc_info:
            service.update_group(
                uuid4(),
                GroupUpdate(display_name="New name"),
            )

        assert exc_info.value.status_code == 404

    def test_delete_group__unknown_group_raises_not_found(self, session):
        with pytest.raises(HTTPException) as exc_info:
            GroupService(session).delete_group(group_id=uuid4())

        assert exc_info.value.status_code == 404

    def test_get_members__returns_members_ordered_by_identity_id(self, session):
        group = GroupFactory()
        user = UserFactory()
        machine_user = MachineUserFactory()

        GroupMembershipFactory(group=group, member=user)
        GroupMembershipFactory(group=group, member=machine_user)

        memberships = GroupService(session).get_members(group.id)

        assert [membership.member_identity_id for membership in memberships] == sorted(
            [user.id, machine_user.id]
        )

        memberships_by_id = {
            membership.member_identity_id: membership for membership in memberships
        }

        user_membership = memberships_by_id[user.id]
        assert user_membership.group_id == group.id
        assert user_membership.member.id == user.id
        assert user_membership.member.external_id == user.external_id
        assert user_membership.member.type == "user"

        machine_user_membership = memberships_by_id[machine_user.id]
        assert machine_user_membership.group_id == group.id
        assert machine_user_membership.member.id == machine_user.id
        assert machine_user_membership.member.external_id == machine_user.external_id
        assert machine_user_membership.member.type == "machine_user"

    def test_get_members__excludes_members_of_other_groups(self, session):
        group = GroupFactory()
        other_group = GroupFactory()
        member = UserFactory()
        other_member = UserFactory()

        GroupMembershipFactory(group=group, member=member)
        GroupMembershipFactory(group=other_group, member=other_member)

        memberships = GroupService(session).get_members(group.id)

        assert len(memberships) == 1
        assert memberships[0].group_id == group.id
        assert memberships[0].member_identity_id == member.id

    def test_get_members__empty_group_returns_empty_list(self, session):
        group = GroupFactory()

        memberships = GroupService(session).get_members(group.id)

        assert memberships == []

    def test_get_members__unknown_group_raises_not_found(self, session):
        with pytest.raises(HTTPException) as exc_info:
            GroupService(session).get_members(uuid4())

        assert exc_info.value.status_code == 404

    def test_replace_members__holds_group_lock_until_transaction_ends(self):
        group = GroupFactory()
        member = UserFactory()

        with (
            Session(bind=engine) as first_session,
            Session(bind=engine) as second_session,
        ):
            with first_session.begin():
                GroupService(first_session).replace_members(
                    group_id=group.id,
                    member_identity_ids=[member.id],
                )

                with pytest.raises(OperationalError) as exc_info:
                    second_session.scalar(
                        select(Group.id)
                        .where(Group.id == group.id)
                        .with_for_update(
                            of=Group,
                            nowait=True,  # NOWAIT to fail inmediately with 55P03
                        )
                    )

                assert exc_info.value.orig.pgcode == "55P03"
                second_session.rollback()

            locked_group_id = second_session.scalar(
                select(Group.id)
                .where(Group.id == group.id)
                .with_for_update(of=Group, nowait=True)
            )

            assert locked_group_id == group.id

    def test_add_members__assigns_membership_policies_in_batch(
        self, authorizer: Authorization, session
    ):
        group = GroupFactory()
        first = UserFactory()
        second = MachineUserFactory()

        GroupService(session).add_members(
            group_id=group.id, member_identity_ids=[first.id, second.id]
        )

        for member in (first, second):
            assert authorizer.has_resource_role(
                user_id=member.id, role_id=group.id, resource_id="*"
            )
            assert authorizer.has_global_role(user_id=member.id, role_id=group.id)

    def test_remove_members__revokes_only_removed_membership_policies(
        self, authorizer: Authorization, session
    ):
        group = GroupFactory()
        removed = UserFactory()
        retained = UserFactory()
        service = GroupService(session)
        service.add_members(
            group_id=group.id, member_identity_ids=[removed.id, retained.id]
        )

        service.remove_members(group_id=group.id, member_identity_ids=[removed.id])

        assert not authorizer.has_resource_role(
            user_id=removed.id, role_id=group.id, resource_id="*"
        )
        assert not authorizer.has_global_role(user_id=removed.id, role_id=group.id)
        assert authorizer.has_resource_role(
            user_id=retained.id, role_id=group.id, resource_id="*"
        )
        assert authorizer.has_global_role(user_id=retained.id, role_id=group.id)

    def test_replace_members__updates_membership_policies(
        self, authorizer: Authorization, session
    ):
        group = GroupFactory()
        removed = UserFactory()
        retained = UserFactory()
        added = UserFactory()
        service = GroupService(session)
        service.add_members(
            group_id=group.id, member_identity_ids=[removed.id, retained.id]
        )

        service.replace_members(
            group_id=group.id, member_identity_ids=[retained.id, added.id]
        )

        assert not authorizer.has_resource_role(
            user_id=removed.id, role_id=group.id, resource_id="*"
        )
        assert not authorizer.has_global_role(user_id=removed.id, role_id=group.id)

        for member in (retained, added):
            assert authorizer.has_resource_role(
                user_id=member.id, role_id=group.id, resource_id="*"
            )
            assert authorizer.has_global_role(user_id=member.id, role_id=group.id)

    def test_create_groups_batch__creates_all_valid_groups(self, session):
        result = GroupService(session).create_groups_batch(
            [
                {"external_id": "engineering", "display_name": "Engineering"},
                {"external_id": "finance", "display_name": "Finance"},
            ]
        )

        groups = session.scalars(select(Group).where(Group.id.in_(result.ids))).all()

        assert len(result.ids) == 2
        assert result.errors == []
        assert {group.external_id for group in groups} == {"engineering", "finance"}

    def test_create_groups_batch__skips_schema_invalid_items(self, session):
        result = GroupService(session).create_groups_batch(
            [
                {"external_id": "engineering", "display_name": "Engineering"},
                {"external_id": "", "display_name": ""},
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].item == {"external_id": "", "display_name": ""}
        assert len(result.errors[0].errors) == 2

    def test_create_groups_batch__skips_existing_external_ids(self, session):
        GroupFactory(external_id="existing")

        result = GroupService(session).create_groups_batch(
            [
                {"external_id": "existing", "display_name": "Existing"},
                {"external_id": "new", "display_name": "New"},
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].errors == [
            "A group with this external ID already exists."
        ]
        assert (
            session.scalar(select(Group).where(Group.id == result.ids[0])).external_id
            == "new"
        )

    def test_create_groups_batch__skips_later_request_duplicate(self, session):
        result = GroupService(session).create_groups_batch(
            [
                {"external_id": "duplicate", "display_name": "First"},
                {"external_id": "duplicate", "display_name": "Second"},
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].errors == [
            "A group with this external ID already exists."
        ]

        group = session.scalar(select(Group).where(Group.id == result.ids[0]))
        assert group.display_name == "First"

    def test_create_groups_batch__returns_all_item_errors(self, session):
        GroupFactory(external_id="existing")

        result = GroupService(session).create_groups_batch(
            [
                {"external_id": "", "display_name": ""},
                {"external_id": "existing", "display_name": "Existing"},
            ]
        )

        assert result.ids == []
        assert len(result.errors) == 2

    def test_delete_groups_batch__deletes_matching_groups(self, session):
        first = GroupFactory()
        second = GroupFactory()
        retained = GroupFactory()

        GroupService(session).delete_groups_batch([first.id, second.id])

        assert session.get(Group, first.id) is None
        assert session.get(Group, second.id) is None
        assert session.get(Group, retained.id) is not None

    def test_delete_groups_batch__ignores_unknown_and_wrong_identity_type_ids(
        self, session
    ):
        group = GroupFactory()
        user = UserFactory()

        GroupService(session).delete_groups_batch([group.id, user.id, uuid4()])

        assert session.get(Group, group.id) is None
        assert user in session

    def test_delete_groups_batch__deletes_memberships_but_retains_members(
        self, session
    ):
        first_group = GroupFactory()
        second_group = GroupFactory()
        first_member = UserFactory()
        second_member = MachineUserFactory()
        service = GroupService(session)
        service.add_members(
            group_id=first_group.id, member_identity_ids=[first_member.id]
        )
        service.add_members(
            group_id=second_group.id, member_identity_ids=[second_member.id]
        )

        service.delete_groups_batch([first_group.id, second_group.id])

        assert not group_has_member(session, first_group.id, first_member.id)
        assert not group_has_member(session, second_group.id, second_member.id)
        assert first_member in session
        assert second_member in session

    def test_delete_groups_batch__clears_subject_and_membership_policies(
        self, authorizer: Authorization, session
    ):
        first_group = GroupFactory()
        second_group = GroupFactory()
        first_member = UserFactory()
        second_member = MachineUserFactory()
        service = GroupService(session)
        service.add_members(
            group_id=first_group.id, member_identity_ids=[first_member.id]
        )
        service.add_members(
            group_id=second_group.id, member_identity_ids=[second_member.id]
        )
        authorizer.assign_global_role(user_id=first_group.id, role_id="first-role")
        authorizer.assign_resource_role(
            user_id=second_group.id, role_id="second-role", resource_id="resource"
        )

        service.delete_groups_batch([first_group.id, second_group.id])

        assert not authorizer.has_global_role(
            user_id=first_group.id, role_id="first-role"
        )
        assert not authorizer.has_resource_role(
            user_id=second_group.id, role_id="second-role", resource_id="resource"
        )
        assert not authorizer.has_global_role(
            user_id=first_member.id, role_id=first_group.id
        )
        assert not authorizer.has_resource_role(
            user_id=first_member.id, role_id=first_group.id, resource_id="*"
        )
        assert not authorizer.has_global_role(
            user_id=second_member.id, role_id=second_group.id
        )
        assert not authorizer.has_resource_role(
            user_id=second_member.id, role_id=second_group.id, resource_id="*"
        )

    def test_delete_group__works_when_group_memberships_are_unloaded(self, session):
        group = GroupFactory()
        member = UserFactory()
        GroupMembershipFactory(group=group, member=member)
        session.flush()
        session.expire(group, ["memberships"])

        GroupService(session).delete_group(group.id)

        assert session.get(Group, group.id) is None
