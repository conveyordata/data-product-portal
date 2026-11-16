from typing import cast
from uuid import uuid4

from sqlalchemy import text  # noqa: TID251

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization, CasbinPolicies
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.database.database import engine
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

ANY: str = "does_not_matter"
ANY_ACT: AuthorizationAction = cast("AuthorizationAction", 0)


class TestHasAccess:
    @staticmethod
    def _consumer_member(status: InputPortStatus):
        member = UserFactory()
        consumer = DataProductFactory()
        DataProductRoleAssignmentFactory(
            identity_id=member.id,
            data_product_id=consumer.id,
            role_id=RoleFactory.data_product_owner().id,
        )
        port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
        InputPortFactory(
            consuming_abstract_data_product=consumer, output_port=port, status=status
        )
        return member, port

    @staticmethod
    def _has_access(session, member, port, act: AuthorizationAction) -> bool:
        return Authorization(session).has_access(
            sub=str(member.id),
            dom=str(port.data_product.domain_id),
            obj=str(port.id),
            parent=str(port.data_product_id),
            act=act,
        )

    def test_has_access__consumer_member_reads_invite_only_output_port(self, session):
        member, port = self._consumer_member(InputPortStatus.APPROVED)

        assert self._has_access(
            session, member, port, AuthorizationAction.HIDDEN__OUTPUT_PORT__READ
        )

    def test_has_access__consumer_member_through_a_group_reads_invite_only_output_port(
        self, session
    ):
        member = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=member)
        consumer = DataProductFactory()
        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=consumer.id,
            role_id=RoleFactory.data_product_owner().id,
        )
        port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
        InputPortFactory(consuming_abstract_data_product=consumer, output_port=port)

        assert self._has_access(
            session, member, port, AuthorizationAction.HIDDEN__OUTPUT_PORT__READ
        )

    def test_has_access__consumer_member_is_denied_another_output_port(self, session):
        member, port = self._consumer_member(InputPortStatus.APPROVED)
        other_port = OutputPortFactory(
            data_product=port.data_product,
            access_function=OutputPortAccessFunction.PRIVATE,
        )

        assert not self._has_access(
            session, member, other_port, AuthorizationAction.HIDDEN__OUTPUT_PORT__READ
        )

    def test_has_access__pending_consumer_is_denied(self, session):
        member, port = self._consumer_member(InputPortStatus.PENDING)

        assert not self._has_access(
            session, member, port, AuthorizationAction.HIDDEN__OUTPUT_PORT__READ
        )

    def test_has_access__consuming_grants_no_other_action(self, session):
        member, port = self._consumer_member(InputPortStatus.APPROVED)

        assert not self._has_access(
            session, member, port, AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES
        )


class TestAuthorization:
    def test_everyone_role(self, authorizer: CasbinPolicies):
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_everyone_role_permissions(actions=[allowed])

        assert authorizer._allows(sub=ANY, dom=ANY, obj=ANY, act=allowed) is True
        assert authorizer._allows(sub=ANY, dom=ANY, obj=ANY, act=denied) is False

        # Clear role definition again
        authorizer.sync_everyone_role_permissions(actions=[])
        assert authorizer._allows(sub=ANY, dom=ANY, obj=ANY, act=allowed) is False

    def test_resource_role(self, authorizer: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=allowed) is True
        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=denied) is False
        assert (
            authorizer._allows(sub=user, dom=ANY, obj="other_resource", act=denied)
            is False
        )

        # Clear role assignment again
        authorizer.revoke_resource_role(user_id=user, role_id=role, resource_id=obj)
        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=allowed) is False

    def test_wildcard_resource_role(self, authorizer: CasbinPolicies):
        role = "public_reader"
        obj = "test_resource"
        allowed = AuthorizationAction.HIDDEN__DATA_PRODUCT__READ
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        authorizer.assign_resource_role(user_id="*", role_id=role, resource_id=obj)

        assert authorizer._allows(sub="user_1", dom=ANY, obj=obj, act=allowed) is True
        assert authorizer._allows(sub="user_2", dom=ANY, obj=obj, act=allowed) is True
        assert authorizer._allows(sub="user_1", dom=ANY, obj=obj, act=denied) is False
        assert (
            authorizer._allows(sub="user_1", dom=ANY, obj="other_resource", act=allowed)
            is False
        )

        authorizer.revoke_resource_role(user_id="*", role_id=role, resource_id=obj)
        assert authorizer._allows(sub="user_1", dom=ANY, obj=obj, act=allowed) is False

    def test_domain_role(self, authorizer: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        dom = "test_domain"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom)

        assert authorizer._allows(sub=user, dom=dom, obj=ANY, act=allowed) is True
        assert authorizer._allows(sub=user, dom=dom, obj=ANY, act=denied) is False
        assert (
            authorizer._allows(sub=user, dom="other_dom", obj=ANY, act=allowed) is False
        )

        # Clear role assignment again
        authorizer.revoke_domain_role(user_id=user, role_id=role, domain_id=dom)
        assert authorizer._allows(sub=user, dom=dom, obj=ANY, act=allowed) is False

    def test_data_product_role_applies_to_output_port(self, authorizer: CasbinPolicies):
        role = "data_product_role"
        user = "test_user"
        data_product = "data_product"
        output_port = "output_port"
        action = AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[action])
        authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=data_product
        )

        assert authorizer._allows(
            sub=user,
            dom=ANY,
            obj=output_port,
            parent=data_product,
            act=action,
        )
        assert not authorizer._allows(
            sub=user,
            dom=ANY,
            obj=output_port,
            parent="other_data_product",
            act=action,
        )

    def test_global_role(self, authorizer: CasbinPolicies, everyone_role_permissions):
        user = "test_user"
        role = "test_role"
        act = AuthorizationAction.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS

        with everyone_role_permissions(permissions=[]):
            authorizer.sync_role_permissions(role_id=role, actions=[act])
            assert authorizer._allows(sub=user, dom=ANY, obj=ANY, act=act) is False

            authorizer.assign_global_role(user_id=user, role_id=role)
            assert authorizer._allows(sub=user, dom=ANY, obj=ANY, act=act) is True

            authorizer.revoke_global_role(user_id=user, role_id=role)
            assert authorizer._allows(sub=user, dom=ANY, obj=ANY, act=act) is False

    def test_admin_role(self, authorizer: CasbinPolicies):
        user = "test_user"

        assert authorizer._allows(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

        authorizer.assign_admin_role(user_id=user)
        assert authorizer._allows(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is True

        authorizer.revoke_admin_role(user_id=user)
        assert authorizer._allows(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

    def test_role_removal(self, authorizer: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=act) is True

        # Clear role assignment again
        authorizer.remove_role_permissions(role_id=role)
        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=act) is False

    def test_multiple_permissions(self, authorizer: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE
        all_acts = list(AuthorizationAction)

        authorizer.sync_role_permissions(role_id=role, actions=all_acts)
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=act) is True

        authorizer.remove_role_permissions(role_id=role)
        assert authorizer._allows(sub=user, dom=ANY, obj=obj, act=act) is False

    def test_clear_assignments_for_resource_role(self, authorizer: CasbinPolicies):
        role1 = "test_role"
        role2 = "other_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role1, actions=[act])
        authorizer.sync_role_permissions(role_id=role2, actions=[act])
        authorizer.assign_resource_role(user_id=user, role_id=role1, resource_id=obj)
        authorizer.assign_resource_role(user_id=user, role_id=role2, resource_id=obj)
        assert authorizer.has_resource_role(
            user_id=user, role_id=role1, resource_id=obj
        )
        assert authorizer.has_resource_role(
            user_id=user, role_id=role2, resource_id=obj
        )

        authorizer.clear_assignments_for_resource_role(role_id=role1)
        assert not authorizer.has_resource_role(
            user_id=user, role_id=role1, resource_id=obj
        )
        assert authorizer.has_resource_role(
            user_id=user, role_id=role2, resource_id=obj
        )

    def test_clear_assignments_for_domain_role(self, authorizer: CasbinPolicies):
        role1 = "test_role"
        role2 = "other_role"
        user = "test_user"
        dom = "test_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role1, actions=[act])
        authorizer.sync_role_permissions(role_id=role2, actions=[act])
        authorizer.assign_domain_role(user_id=user, role_id=role1, domain_id=dom)
        authorizer.assign_domain_role(user_id=user, role_id=role2, domain_id=dom)
        assert authorizer.has_domain_role(user_id=user, role_id=role1, domain_id=dom)
        assert authorizer.has_domain_role(user_id=user, role_id=role2, domain_id=dom)

        authorizer.clear_assignments_for_domain_role(role_id=role1)
        assert not authorizer.has_domain_role(
            user_id=user, role_id=role1, domain_id=dom
        )
        assert authorizer.has_domain_role(user_id=user, role_id=role2, domain_id=dom)

    def test_clear_assignments_for_global_role(self, authorizer: CasbinPolicies):
        role1 = "test_role"
        role2 = "other_role"
        user = "test_user"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role1, actions=[act])
        authorizer.sync_role_permissions(role_id=role2, actions=[act])
        authorizer.assign_global_role(user_id=user, role_id=role1)
        authorizer.assign_global_role(user_id=user, role_id=role2)
        assert authorizer.has_global_role(user_id=user, role_id=role1)
        assert authorizer.has_global_role(user_id=user, role_id=role2)

        authorizer.clear_assignments_for_global_role(role_id=role1)
        assert not authorizer.has_global_role(user_id=user, role_id=role1)
        assert authorizer.has_global_role(user_id=user, role_id=role2)

    def test_clear_assignments_for_user(self, authorizer: CasbinPolicies):
        role = "test_role"
        user1 = "test_user"
        user2 = "other_user"
        obj = "test_resource"
        dom = "test_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        authorizer.assign_resource_role(user_id=user1, role_id=role, resource_id=obj)
        assert authorizer.has_resource_role(
            user_id=user1, role_id=role, resource_id=obj
        )
        authorizer.assign_domain_role(user_id=user1, role_id=role, domain_id=dom)
        assert authorizer.has_domain_role(user_id=user1, role_id=role, domain_id=dom)

        authorizer.assign_resource_role(user_id=user2, role_id=role, resource_id=obj)
        assert authorizer.has_resource_role(
            user_id=user2, role_id=role, resource_id=obj
        )

        authorizer.clear_assignments_for_user(user_id=user1)
        assert not authorizer.has_resource_role(
            user_id=user1, role_id=role, resource_id=obj
        )
        assert not authorizer.has_domain_role(
            user_id=user1, role_id=role, domain_id=dom
        )
        assert authorizer.has_resource_role(
            user_id=user2, role_id=role, resource_id=obj
        )

    def test_clear_assignments_for_resource(self, authorizer: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj1 = "test_resource"
        obj2 = "other_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj1)
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj2)
        assert authorizer.has_resource_role(
            user_id=user, role_id=role, resource_id=obj1
        )
        assert authorizer.has_resource_role(
            user_id=user, role_id=role, resource_id=obj2
        )

        authorizer.clear_assignments_for_resource(resource_id=obj1)
        assert not authorizer.has_resource_role(
            user_id=user, role_id=role, resource_id=obj1
        )
        assert authorizer.has_resource_role(
            user_id=user, role_id=role, resource_id=obj2
        )

    def test_clear_assignments_for_domain(self, authorizer: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        dom1 = "test_domain"
        dom2 = "other_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom1)
        authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom2)

        authorizer.clear_assignments_for_domain(domain_id=dom1)
        assert not authorizer.has_domain_role(
            user_id=user, role_id=role, domain_id=dom1
        )
        assert authorizer.has_domain_role(user_id=user, role_id=role, domain_id=dom2)

    def test_resource_role_inherited_from_group(self, authorizer: CasbinPolicies):
        user = "test_user"
        group = "test_group"
        role = "test_role"
        dp1 = "test_data_product"
        dp2 = "other_data_product"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[action])
        authorizer.assign_resource_role(
            user_id=group,
            role_id=role,
            resource_id=dp1,
        )
        authorizer.assign_group_memberships(memberships=[(user, group)])

        assert authorizer.has_resource_role(
            user_id=user,
            role_id=group,
            resource_id="*",
        )
        assert not authorizer.has_resource_role(
            user_id=user,
            role_id=group,
            resource_id=dp1,
        )

        assert authorizer._allows(
            sub=user,
            dom=ANY,
            obj=dp1,
            act=action,
        )
        assert not authorizer._allows(
            sub=user,
            dom=ANY,
            obj=dp2,
            act=action,
        )

        authorizer.revoke_group_memberships(memberships=[(user, group)])
        assert not authorizer._allows(
            sub=user,
            dom=ANY,
            obj=dp1,
            act=action,
        )

    def test_global_role_inherited_from_group(
        self,
        authorizer: CasbinPolicies,
        everyone_role_permissions,
    ):
        user = "test_user"
        group = "test_group"
        role = "test_role"
        action = AuthorizationAction.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS

        with everyone_role_permissions(permissions=[]):
            authorizer.sync_role_permissions(role_id=role, actions=[action])
            authorizer.assign_global_role(user_id=group, role_id=role)
            authorizer.assign_group_memberships(memberships=[(user, group)])

            assert authorizer._allows(
                sub=user,
                dom=ANY,
                obj=ANY,
                act=action,
            )

            authorizer.revoke_group_memberships(memberships=[(user, group)])

            assert not authorizer._allows(
                sub=user,
                dom=ANY,
                obj=ANY,
                act=action,
            )

    def test_group_role_added_after_membership_is_inherited(
        self,
        authorizer: CasbinPolicies,
    ):
        user = "test_user"
        group = "test_group"
        role = "test_role"
        data_product = "test_data_product"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[action])

        # Membership exists before the group receives the role.
        authorizer.assign_group_memberships(memberships=[(user, group)])
        assert not authorizer._allows(
            sub=user,
            dom=ANY,
            obj=data_product,
            act=action,
        )

        authorizer.assign_resource_role(
            user_id=group,
            role_id=role,
            resource_id=data_product,
        )
        assert authorizer._allows(
            sub=user,
            dom=ANY,
            obj=data_product,
            act=action,
        )

        authorizer.revoke_resource_role(
            user_id=group,
            role_id=role,
            resource_id=data_product,
        )
        assert not authorizer._allows(
            sub=user,
            dom=ANY,
            obj=data_product,
            act=action,
        )

    def test_assign_group_memberships__assigns_resource_and_global_memberships(
        self, authorizer: CasbinPolicies
    ):
        memberships = [
            ("first-user", "first-group"),
            ("second-user", "second-group"),
        ]

        updated = authorizer.assign_group_memberships(memberships=memberships)

        assert updated
        for member_id, group_id in memberships:
            assert authorizer.has_resource_role(
                user_id=member_id, role_id=group_id, resource_id="*"
            )
            assert authorizer.has_global_role(user_id=member_id, role_id=group_id)

    def test_assign_group_memberships__empty_list_does_nothing(
        self, authorizer: CasbinPolicies
    ):
        assert not authorizer.assign_group_memberships(memberships=[])

    def test_assign_group_memberships__existing_memberships_are_ignored(
        self, authorizer: CasbinPolicies
    ):
        memberships = [("user", "group")]
        authorizer.assign_group_memberships(memberships=memberships)

        updated = authorizer.assign_group_memberships(memberships=memberships)

        assert not updated
        assert authorizer.has_resource_role(
            user_id="user", role_id="group", resource_id="*"
        )
        assert authorizer.has_global_role(user_id="user", role_id="group")

    def test_assign_group_memberships__adds_missing_policy_from_mixed_batch(
        self, authorizer: CasbinPolicies
    ):
        existing = ("existing-user", "existing-group")
        missing = ("missing-user", "missing-group")
        authorizer.assign_group_memberships(memberships=[existing])

        updated = authorizer.assign_group_memberships(memberships=[existing, missing])

        assert updated
        for member_id, group_id in (existing, missing):
            assert authorizer.has_resource_role(
                user_id=member_id,
                role_id=group_id,
                resource_id="*",
            )
            assert authorizer.has_global_role(
                user_id=member_id,
                role_id=group_id,
            )

    def test_revoke_group_memberships__revokes_resource_and_global_memberships(
        self, authorizer: CasbinPolicies
    ):
        memberships = [
            ("first-user", "first-group"),
            ("second-user", "second-group"),
        ]
        authorizer.assign_group_memberships(memberships=memberships)

        updated = authorizer.revoke_group_memberships(memberships=memberships)

        assert updated
        for member_id, group_id in memberships:
            assert not authorizer.has_resource_role(
                user_id=member_id, role_id=group_id, resource_id="*"
            )
            assert not authorizer.has_global_role(user_id=member_id, role_id=group_id)

    def test_assign_group_memberships__reconciles_policies_from_another_worker(
        self, authorizer: CasbinPolicies
    ):
        suffix = uuid4().hex
        persisted_elsewhere = (
            f"remote-user-{suffix}",
            f"remote-group-{suffix}",
        )
        new_membership = (
            f"new-user-{suffix}",
            f"new-group-{suffix}",
        )

        self._persist_group_membership(*persisted_elsewhere)

        assert not authorizer.has_resource_role(
            user_id=persisted_elsewhere[0],
            role_id=persisted_elsewhere[1],
            resource_id="*",
        )

        updated = authorizer.assign_group_memberships(
            memberships=[persisted_elsewhere, new_membership]
        )

        assert updated
        for member_id, group_id in (persisted_elsewhere, new_membership):
            assert self._count_group_membership_policies(member_id, group_id) == 2
            assert authorizer.has_resource_role(
                user_id=member_id,
                role_id=group_id,
                resource_id="*",
            )
            assert authorizer.has_global_role(
                user_id=member_id,
                role_id=group_id,
            )

    def test_revoke_group_memberships__does_not_remove_unrelated_memberships(
        self, authorizer: CasbinPolicies
    ):
        removed = ("removed-user", "removed-group")
        retained = ("retained-user", "retained-group")
        authorizer.assign_group_memberships(memberships=[removed, retained])

        authorizer.revoke_group_memberships(memberships=[removed])

        assert not authorizer.has_resource_role(
            user_id=removed[0], role_id=removed[1], resource_id="*"
        )
        assert not authorizer.has_global_role(user_id=removed[0], role_id=removed[1])
        assert authorizer.has_resource_role(
            user_id=retained[0], role_id=retained[1], resource_id="*"
        )
        assert authorizer.has_global_role(user_id=retained[0], role_id=retained[1])

    def test_revoke_group_memberships__removes_present_policy_from_mixed_batch(
        self, authorizer: CasbinPolicies
    ):
        existing = ("existing-user", "existing-group")
        missing = ("missing-user", "missing-group")
        authorizer.assign_group_memberships(memberships=[existing])

        updated = authorizer.revoke_group_memberships(memberships=[missing, existing])

        assert updated
        assert not authorizer.has_resource_role(
            user_id=existing[0],
            role_id=existing[1],
            resource_id="*",
        )
        assert not authorizer.has_global_role(
            user_id=existing[0],
            role_id=existing[1],
        )

    def test_revoke_group_memberships__reconciles_policies_from_another_worker(
        self, authorizer: CasbinPolicies
    ):
        suffix = uuid4().hex
        locally_known = (
            f"local-user-{suffix}",
            f"local-group-{suffix}",
        )
        persisted_elsewhere = (
            f"remote-user-{suffix}",
            f"remote-group-{suffix}",
        )

        authorizer.assign_group_memberships(memberships=[locally_known])
        self._persist_group_membership(*persisted_elsewhere)

        assert not authorizer.has_resource_role(
            user_id=persisted_elsewhere[0],
            role_id=persisted_elsewhere[1],
            resource_id="*",
        )

        updated = authorizer.revoke_group_memberships(
            memberships=[persisted_elsewhere, locally_known]
        )

        assert updated
        for member_id, group_id in (persisted_elsewhere, locally_known):
            assert self._count_group_membership_policies(member_id, group_id) == 0
            assert not authorizer.has_resource_role(
                user_id=member_id,
                role_id=group_id,
                resource_id="*",
            )
            assert not authorizer.has_global_role(
                user_id=member_id,
                role_id=group_id,
            )

    def test_revoke_group_memberships__empty_list_does_nothing(
        self, authorizer: CasbinPolicies
    ):
        assert not authorizer.revoke_group_memberships(memberships=[])

    def test_clear_assignments_for_identities__clears_all_assignment_types(
        self,
        authorizer: CasbinPolicies,
    ):
        removed = ["first-user", "second-user"]
        retained = "retained-user"

        for user in removed:
            authorizer.assign_resource_role(
                user_id=user,
                role_id="resource-role",
                resource_id="resource",
            )
            authorizer.assign_domain_role(
                user_id=user,
                role_id="domain-role",
                domain_id="domain",
            )
            authorizer.assign_global_role(
                user_id=user,
                role_id="global-role",
            )

        authorizer.assign_global_role(
            user_id=retained,
            role_id="retained-role",
        )

        updated = authorizer.clear_assignments_for_identities(identity_ids=removed)

        assert updated
        for user in removed:
            assert not authorizer.has_resource_role(
                user_id=user,
                role_id="resource-role",
                resource_id="resource",
            )
            assert not authorizer.has_domain_role(
                user_id=user,
                role_id="domain-role",
                domain_id="domain",
            )
            assert not authorizer.has_global_role(
                user_id=user,
                role_id="global-role",
            )

        assert authorizer.has_global_role(
            user_id=retained,
            role_id="retained-role",
        )

    def test_clear_assignments_for_identities__empty_list_does_nothing(
        self,
        authorizer: CasbinPolicies,
    ):
        assert not authorizer.clear_assignments_for_identities(identity_ids=[])

    def test_clear_assignments_for_identities__removes_policy_from_another_worker(
        self, authorizer: CasbinPolicies
    ):
        suffix = uuid4().hex
        user = f"remote-user-{suffix}"
        role = f"remote-role-{suffix}"
        resource = f"remote-resource-{suffix}"

        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO casbin_rule (ptype, v0, v1, v2)
                    VALUES ('g', :user, :role, :resource)
                    """
                ),
                {
                    "user": user,
                    "role": role,
                    "resource": resource,
                },
            )

        # The policy was persisted by another worker and is absent locally.
        assert not authorizer.has_resource_role(
            user_id=user,
            role_id=role,
            resource_id=resource,
        )

        updated = authorizer.clear_assignments_for_identities(identity_ids=[user])

        assert updated
        assert not authorizer.has_resource_role(
            user_id=user,
            role_id=role,
            resource_id=resource,
        )

        with engine.connect() as connection:
            remaining = connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM casbin_rule
                    WHERE ptype = 'g'
                      AND v0 = :user
                      AND v1 = :role
                      AND v2 = :resource
                    """
                ),
                {
                    "user": user,
                    "role": role,
                    "resource": resource,
                },
            ).scalar_one()

        assert remaining == 0

    def _persist_group_membership(self, member_id: str, group_id: str) -> None:
        """
        Simulate another Casbin worker persisting policies without updating this
        worker's in-memory state.
        """
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO casbin_rule (ptype, v0, v1, v2)
                    VALUES ('g', :member_id, :group_id, '*')
                    """
                ),
                {
                    "member_id": member_id,
                    "group_id": group_id,
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO casbin_rule (ptype, v0, v1)
                    VALUES ('g3', :member_id, :group_id)
                    """
                ),
                {
                    "member_id": member_id,
                    "group_id": group_id,
                },
            )

    def _count_group_membership_policies(self, member_id: str, group_id: str) -> int:
        with engine.connect() as connection:
            return connection.execute(
                text(
                    """
                    SELECT COUNT(*)
                    FROM casbin_rule
                    WHERE v0 = :member_id
                      AND v1 = :group_id
                      AND (
                        (ptype = 'g' AND v2 = '*')
                            OR ptype = 'g3'
                        )
                    """
                ),
                {
                    "member_id": member_id,
                    "group_id": group_id,
                },
            ).scalar_one()


class TestCrossWorkerStaleness:
    def test_auto_reload_resolves_stale_policy(self, authorizer: CasbinPolicies):
        """Regression test: a role assigned by another worker (direct DB write) is
        invisible until the enforcer reloads and the TTL cache expires."""
        role = "staleness_role"
        user = "staleness_user"
        resource = "staleness_resource"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[action])
        assert authorizer._allows(sub=user, dom="*", obj=resource, act=action) is False

        # Another worker writes the assignment directly to DB, bypassing the enforcer
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO casbin_rule (ptype, v0, v1, v2) "
                    "VALUES ('g', :u, :r, :obj)"
                ),
                {"u": user, "r": role, "obj": resource},
            )

        # In-memory is stale: still denied despite the DB change
        assert authorizer._allows(sub=user, dom="*", obj=resource, act=action) is False

        # Simulate start_auto_load_policy firing and the TTL cache expiring
        authorizer._enforcer.load_policy()
        authorizer._cache.clear()

        # Access is now correctly granted
        assert authorizer._allows(sub=user, dom="*", obj=resource, act=action) is True

        # Cleanup
        with engine.begin() as conn:
            conn.execute(
                text(
                    "DELETE FROM casbin_rule "
                    "WHERE ptype='g' AND v0=:u AND v1=:r AND v2=:obj"
                ),
                {"u": user, "r": role, "obj": resource},
            )
        authorizer.remove_role_permissions(role_id=role)
