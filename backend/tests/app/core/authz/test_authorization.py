from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import text  # noqa: TID251

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization, CasbinPolicies
from app.core.authz.rules import (
    GlobalRole,
    Permission,
    ResourceRole,
    Rule,
    membership_rules,
)
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
    def _has_access(session, member, port, act: AuthorizationAction) -> bool:
        return Authorization(session).has_access(
            sub=str(member.id),
            dom=str(port.data_product.domain_id),
            obj=str(port.id),
            parent=str(port.data_product_id),
            act=act,
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

    def test_has_access__consuming_grants_no_other_action(self, session):
        member = UserFactory()
        consumer = DataProductFactory()
        DataProductRoleAssignmentFactory(
            identity_id=member.id,
            data_product_id=consumer.id,
            role_id=RoleFactory.data_product_owner().id,
        )
        port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)
        InputPortFactory(consuming_abstract_data_product=consumer, output_port=port)

        assert not self._has_access(
            session, member, port, AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES
        )


class TestAuthorization:
    def test_everyone_role(self, policies: CasbinPolicies):
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        policies.sync_everyone_role_permissions(actions=[allowed])

        assert policies.allows(sub=ANY, dom=ANY, obj=ANY, act=allowed) is True
        assert policies.allows(sub=ANY, dom=ANY, obj=ANY, act=denied) is False

        # Clear role definition again
        policies.sync_everyone_role_permissions(actions=[])
        assert policies.allows(sub=ANY, dom=ANY, obj=ANY, act=allowed) is False

    def test_resource_role(self, policies: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        policies.sync_role_permissions(role_id=role, actions=[allowed])
        policies.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert policies.allows(sub=user, dom=ANY, obj=obj, act=allowed) is True
        assert policies.allows(sub=user, dom=ANY, obj=obj, act=denied) is False
        assert (
            policies.allows(sub=user, dom=ANY, obj="other_resource", act=denied)
            is False
        )

        # Clear role assignment again
        policies.revoke_resource_role(user_id=user, role_id=role, resource_id=obj)
        assert policies.allows(sub=user, dom=ANY, obj=obj, act=allowed) is False

    def test_wildcard_resource_role(self, policies: CasbinPolicies):
        role = "public_reader"
        obj = "test_resource"
        allowed = AuthorizationAction.HIDDEN__DATA_PRODUCT__READ
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        policies.sync_role_permissions(role_id=role, actions=[allowed])
        policies.assign_resource_role(user_id="*", role_id=role, resource_id=obj)

        assert policies.allows(sub="user_1", dom=ANY, obj=obj, act=allowed) is True
        assert policies.allows(sub="user_2", dom=ANY, obj=obj, act=allowed) is True
        assert policies.allows(sub="user_1", dom=ANY, obj=obj, act=denied) is False
        assert (
            policies.allows(sub="user_1", dom=ANY, obj="other_resource", act=allowed)
            is False
        )

        policies.revoke_resource_role(user_id="*", role_id=role, resource_id=obj)
        assert policies.allows(sub="user_1", dom=ANY, obj=obj, act=allowed) is False

    def test_domain_role(self, policies: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        dom = "test_domain"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        policies.sync_role_permissions(role_id=role, actions=[allowed])
        policies.assign_domain_role(user_id=user, role_id=role, domain_id=dom)

        assert policies.allows(sub=user, dom=dom, obj=ANY, act=allowed) is True
        assert policies.allows(sub=user, dom=dom, obj=ANY, act=denied) is False
        assert policies.allows(sub=user, dom="other_dom", obj=ANY, act=allowed) is False

        # Clear role assignment again
        policies.revoke_domain_role(user_id=user, role_id=role, domain_id=dom)
        assert policies.allows(sub=user, dom=dom, obj=ANY, act=allowed) is False

    def test_data_product_role_applies_to_output_port(self, policies: CasbinPolicies):
        role = "data_product_role"
        user = "test_user"
        data_product = "data_product"
        output_port = "output_port"
        action = AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES

        policies.sync_role_permissions(role_id=role, actions=[action])
        policies.assign_resource_role(
            user_id=user, role_id=role, resource_id=data_product
        )

        assert policies.allows(
            sub=user,
            dom=ANY,
            obj=output_port,
            parent=data_product,
            act=action,
        )
        assert not policies.allows(
            sub=user,
            dom=ANY,
            obj=output_port,
            parent="other_data_product",
            act=action,
        )

    def test_global_role(self, policies: CasbinPolicies, everyone_role_permissions):
        user = "test_user"
        role = "test_role"
        act = AuthorizationAction.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS

        with everyone_role_permissions(permissions=[]):
            policies.sync_role_permissions(role_id=role, actions=[act])
            assert policies.allows(sub=user, dom=ANY, obj=ANY, act=act) is False

            policies.assign_global_role(user_id=user, role_id=role)
            assert policies.allows(sub=user, dom=ANY, obj=ANY, act=act) is True

            policies.revoke_global_role(user_id=user, role_id=role)
            assert policies.allows(sub=user, dom=ANY, obj=ANY, act=act) is False

    def test_admin_role(self, policies: CasbinPolicies):
        user = "test_user"

        assert policies.allows(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

        policies.assign_admin_role(user_id=user)
        assert policies.allows(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is True

        policies.revoke_admin_role(user_id=user)
        assert policies.allows(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

    def test_role_removal(self, policies: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        policies.sync_role_permissions(role_id=role, actions=[act])
        policies.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert policies.allows(sub=user, dom=ANY, obj=obj, act=act) is True

        # Clear role assignment again
        policies.remove_role_permissions(role_id=role)
        assert policies.allows(sub=user, dom=ANY, obj=obj, act=act) is False

    def test_multiple_permissions(self, policies: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE
        all_acts = list(AuthorizationAction)

        policies.sync_role_permissions(role_id=role, actions=all_acts)
        policies.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert policies.allows(sub=user, dom=ANY, obj=obj, act=act) is True

        policies.remove_role_permissions(role_id=role)
        assert policies.allows(sub=user, dom=ANY, obj=obj, act=act) is False

    def test_clear_assignments_for_resource_role(self, policies: CasbinPolicies):
        role1 = "test_role"
        role2 = "other_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        policies.sync_role_permissions(role_id=role1, actions=[act])
        policies.sync_role_permissions(role_id=role2, actions=[act])
        policies.assign_resource_role(user_id=user, role_id=role1, resource_id=obj)
        policies.assign_resource_role(user_id=user, role_id=role2, resource_id=obj)
        assert policies.has_resource_role(user_id=user, role_id=role1, resource_id=obj)
        assert policies.has_resource_role(user_id=user, role_id=role2, resource_id=obj)

        policies.clear_assignments_for_resource_role(role_id=role1)
        assert not policies.has_resource_role(
            user_id=user, role_id=role1, resource_id=obj
        )
        assert policies.has_resource_role(user_id=user, role_id=role2, resource_id=obj)

    def test_clear_assignments_for_domain_role(self, policies: CasbinPolicies):
        role1 = "test_role"
        role2 = "other_role"
        user = "test_user"
        dom = "test_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        policies.sync_role_permissions(role_id=role1, actions=[act])
        policies.sync_role_permissions(role_id=role2, actions=[act])
        policies.assign_domain_role(user_id=user, role_id=role1, domain_id=dom)
        policies.assign_domain_role(user_id=user, role_id=role2, domain_id=dom)
        assert policies.has_domain_role(user_id=user, role_id=role1, domain_id=dom)
        assert policies.has_domain_role(user_id=user, role_id=role2, domain_id=dom)

        policies.clear_assignments_for_domain_role(role_id=role1)
        assert not policies.has_domain_role(user_id=user, role_id=role1, domain_id=dom)
        assert policies.has_domain_role(user_id=user, role_id=role2, domain_id=dom)

    def test_clear_assignments_for_global_role(self, policies: CasbinPolicies):
        role1 = "test_role"
        role2 = "other_role"
        user = "test_user"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        policies.sync_role_permissions(role_id=role1, actions=[act])
        policies.sync_role_permissions(role_id=role2, actions=[act])
        policies.assign_global_role(user_id=user, role_id=role1)
        policies.assign_global_role(user_id=user, role_id=role2)
        assert policies.has_global_role(user_id=user, role_id=role1)
        assert policies.has_global_role(user_id=user, role_id=role2)

        policies.clear_assignments_for_global_role(role_id=role1)
        assert not policies.has_global_role(user_id=user, role_id=role1)
        assert policies.has_global_role(user_id=user, role_id=role2)

    def test_clear_assignments_for_user(self, policies: CasbinPolicies):
        role = "test_role"
        user1 = "test_user"
        user2 = "other_user"
        obj = "test_resource"
        dom = "test_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        policies.sync_role_permissions(role_id=role, actions=[act])
        policies.assign_resource_role(user_id=user1, role_id=role, resource_id=obj)
        assert policies.has_resource_role(user_id=user1, role_id=role, resource_id=obj)
        policies.assign_domain_role(user_id=user1, role_id=role, domain_id=dom)
        assert policies.has_domain_role(user_id=user1, role_id=role, domain_id=dom)

        policies.assign_resource_role(user_id=user2, role_id=role, resource_id=obj)
        assert policies.has_resource_role(user_id=user2, role_id=role, resource_id=obj)

        policies.clear_assignments_for_user(user_id=user1)
        assert not policies.has_resource_role(
            user_id=user1, role_id=role, resource_id=obj
        )
        assert not policies.has_domain_role(user_id=user1, role_id=role, domain_id=dom)
        assert policies.has_resource_role(user_id=user2, role_id=role, resource_id=obj)

    def test_clear_assignments_for_resource(self, policies: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        obj1 = "test_resource"
        obj2 = "other_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        policies.sync_role_permissions(role_id=role, actions=[act])
        policies.assign_resource_role(user_id=user, role_id=role, resource_id=obj1)
        policies.assign_resource_role(user_id=user, role_id=role, resource_id=obj2)
        assert policies.has_resource_role(user_id=user, role_id=role, resource_id=obj1)
        assert policies.has_resource_role(user_id=user, role_id=role, resource_id=obj2)

        policies.clear_assignments_for_resource(resource_id=obj1)
        assert not policies.has_resource_role(
            user_id=user, role_id=role, resource_id=obj1
        )
        assert policies.has_resource_role(user_id=user, role_id=role, resource_id=obj2)

    def test_clear_assignments_for_domain(self, policies: CasbinPolicies):
        role = "test_role"
        user = "test_user"
        dom1 = "test_domain"
        dom2 = "other_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        policies.sync_role_permissions(role_id=role, actions=[act])
        policies.assign_domain_role(user_id=user, role_id=role, domain_id=dom1)
        policies.assign_domain_role(user_id=user, role_id=role, domain_id=dom2)

        policies.clear_assignments_for_domain(domain_id=dom1)
        assert not policies.has_domain_role(user_id=user, role_id=role, domain_id=dom1)
        assert policies.has_domain_role(user_id=user, role_id=role, domain_id=dom2)

    def test_resource_role_inherited_from_group(self, policies: CasbinPolicies):
        user = "test_user"
        group = "test_group"
        role = "test_role"
        dp1 = "test_data_product"
        dp2 = "other_data_product"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        policies.sync_role_permissions(role_id=role, actions=[action])
        policies.assign_resource_role(
            user_id=group,
            role_id=role,
            resource_id=dp1,
        )
        policies.assign_group_memberships(memberships=[(user, group)])

        assert policies.has_resource_role(
            user_id=user,
            role_id=group,
            resource_id="*",
        )
        assert not policies.has_resource_role(
            user_id=user,
            role_id=group,
            resource_id=dp1,
        )

        assert policies.allows(
            sub=user,
            dom=ANY,
            obj=dp1,
            act=action,
        )
        assert not policies.allows(
            sub=user,
            dom=ANY,
            obj=dp2,
            act=action,
        )

        policies.revoke_group_memberships(memberships=[(user, group)])
        assert not policies.allows(
            sub=user,
            dom=ANY,
            obj=dp1,
            act=action,
        )

    def test_global_role_inherited_from_group(
        self,
        policies: CasbinPolicies,
        everyone_role_permissions,
    ):
        user = "test_user"
        group = "test_group"
        role = "test_role"
        action = AuthorizationAction.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS

        with everyone_role_permissions(permissions=[]):
            policies.sync_role_permissions(role_id=role, actions=[action])
            policies.assign_global_role(user_id=group, role_id=role)
            policies.assign_group_memberships(memberships=[(user, group)])

            assert policies.allows(
                sub=user,
                dom=ANY,
                obj=ANY,
                act=action,
            )

            policies.revoke_group_memberships(memberships=[(user, group)])

            assert not policies.allows(
                sub=user,
                dom=ANY,
                obj=ANY,
                act=action,
            )

    def test_group_role_added_after_membership_is_inherited(
        self,
        policies: CasbinPolicies,
    ):
        user = "test_user"
        group = "test_group"
        role = "test_role"
        data_product = "test_data_product"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        policies.sync_role_permissions(role_id=role, actions=[action])

        # Membership exists before the group receives the role.
        policies.assign_group_memberships(memberships=[(user, group)])
        assert not policies.allows(
            sub=user,
            dom=ANY,
            obj=data_product,
            act=action,
        )

        policies.assign_resource_role(
            user_id=group,
            role_id=role,
            resource_id=data_product,
        )
        assert policies.allows(
            sub=user,
            dom=ANY,
            obj=data_product,
            act=action,
        )

        policies.revoke_resource_role(
            user_id=group,
            role_id=role,
            resource_id=data_product,
        )
        assert not policies.allows(
            sub=user,
            dom=ANY,
            obj=data_product,
            act=action,
        )

    def test_assign_group_memberships__assigns_resource_and_global_memberships(
        self, policies: CasbinPolicies
    ):
        memberships = [
            ("first-user", "first-group"),
            ("second-user", "second-group"),
        ]

        updated = policies.assign_group_memberships(memberships=memberships)

        assert updated
        for member_id, group_id in memberships:
            assert policies.has_resource_role(
                user_id=member_id, role_id=group_id, resource_id="*"
            )
            assert policies.has_global_role(user_id=member_id, role_id=group_id)

    def test_assign_group_memberships__empty_list_does_nothing(
        self, policies: CasbinPolicies
    ):
        assert not policies.assign_group_memberships(memberships=[])

    def test_assign_group_memberships__existing_memberships_are_ignored(
        self, policies: CasbinPolicies
    ):
        memberships = [("user", "group")]
        policies.assign_group_memberships(memberships=memberships)

        updated = policies.assign_group_memberships(memberships=memberships)

        assert not updated
        assert policies.has_resource_role(
            user_id="user", role_id="group", resource_id="*"
        )
        assert policies.has_global_role(user_id="user", role_id="group")

    def test_assign_group_memberships__adds_missing_policy_from_mixed_batch(
        self, policies: CasbinPolicies
    ):
        existing = ("existing-user", "existing-group")
        missing = ("missing-user", "missing-group")
        policies.assign_group_memberships(memberships=[existing])

        updated = policies.assign_group_memberships(memberships=[existing, missing])

        assert updated
        for member_id, group_id in (existing, missing):
            assert policies.has_resource_role(
                user_id=member_id,
                role_id=group_id,
                resource_id="*",
            )
            assert policies.has_global_role(
                user_id=member_id,
                role_id=group_id,
            )

    def test_revoke_group_memberships__revokes_resource_and_global_memberships(
        self, policies: CasbinPolicies
    ):
        memberships = [
            ("first-user", "first-group"),
            ("second-user", "second-group"),
        ]
        policies.assign_group_memberships(memberships=memberships)

        updated = policies.revoke_group_memberships(memberships=memberships)

        assert updated
        for member_id, group_id in memberships:
            assert not policies.has_resource_role(
                user_id=member_id, role_id=group_id, resource_id="*"
            )
            assert not policies.has_global_role(user_id=member_id, role_id=group_id)

    def test_assign_group_memberships__reconciles_policies_from_another_worker(
        self, policies: CasbinPolicies
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

        assert not policies.has_resource_role(
            user_id=persisted_elsewhere[0],
            role_id=persisted_elsewhere[1],
            resource_id="*",
        )

        updated = policies.assign_group_memberships(
            memberships=[persisted_elsewhere, new_membership]
        )

        assert updated
        for member_id, group_id in (persisted_elsewhere, new_membership):
            assert self._count_group_membership_policies(member_id, group_id) == 2
            assert policies.has_resource_role(
                user_id=member_id,
                role_id=group_id,
                resource_id="*",
            )
            assert policies.has_global_role(
                user_id=member_id,
                role_id=group_id,
            )

    def test_revoke_group_memberships__does_not_remove_unrelated_memberships(
        self, policies: CasbinPolicies
    ):
        removed = ("removed-user", "removed-group")
        retained = ("retained-user", "retained-group")
        policies.assign_group_memberships(memberships=[removed, retained])

        policies.revoke_group_memberships(memberships=[removed])

        assert not policies.has_resource_role(
            user_id=removed[0], role_id=removed[1], resource_id="*"
        )
        assert not policies.has_global_role(user_id=removed[0], role_id=removed[1])
        assert policies.has_resource_role(
            user_id=retained[0], role_id=retained[1], resource_id="*"
        )
        assert policies.has_global_role(user_id=retained[0], role_id=retained[1])

    def test_revoke_group_memberships__removes_present_policy_from_mixed_batch(
        self, policies: CasbinPolicies
    ):
        existing = ("existing-user", "existing-group")
        missing = ("missing-user", "missing-group")
        policies.assign_group_memberships(memberships=[existing])

        updated = policies.revoke_group_memberships(memberships=[missing, existing])

        assert updated
        assert not policies.has_resource_role(
            user_id=existing[0],
            role_id=existing[1],
            resource_id="*",
        )
        assert not policies.has_global_role(
            user_id=existing[0],
            role_id=existing[1],
        )

    def test_revoke_group_memberships__reconciles_policies_from_another_worker(
        self, policies: CasbinPolicies
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

        policies.assign_group_memberships(memberships=[locally_known])
        self._persist_group_membership(*persisted_elsewhere)

        assert not policies.has_resource_role(
            user_id=persisted_elsewhere[0],
            role_id=persisted_elsewhere[1],
            resource_id="*",
        )

        updated = policies.revoke_group_memberships(
            memberships=[persisted_elsewhere, locally_known]
        )

        assert updated
        for member_id, group_id in (persisted_elsewhere, locally_known):
            assert self._count_group_membership_policies(member_id, group_id) == 0
            assert not policies.has_resource_role(
                user_id=member_id,
                role_id=group_id,
                resource_id="*",
            )
            assert not policies.has_global_role(
                user_id=member_id,
                role_id=group_id,
            )

    def test_revoke_group_memberships__empty_list_does_nothing(
        self, policies: CasbinPolicies
    ):
        assert not policies.revoke_group_memberships(memberships=[])

    def test_clear_assignments_for_identities__clears_all_assignment_types(
        self,
        policies: CasbinPolicies,
    ):
        removed = ["first-user", "second-user"]
        retained = "retained-user"

        for user in removed:
            policies.assign_resource_role(
                user_id=user,
                role_id="resource-role",
                resource_id="resource",
            )
            policies.assign_domain_role(
                user_id=user,
                role_id="domain-role",
                domain_id="domain",
            )
            policies.assign_global_role(
                user_id=user,
                role_id="global-role",
            )

        policies.assign_global_role(
            user_id=retained,
            role_id="retained-role",
        )

        updated = policies.clear_assignments_for_identities(identity_ids=removed)

        assert updated
        for user in removed:
            assert not policies.has_resource_role(
                user_id=user,
                role_id="resource-role",
                resource_id="resource",
            )
            assert not policies.has_domain_role(
                user_id=user,
                role_id="domain-role",
                domain_id="domain",
            )
            assert not policies.has_global_role(
                user_id=user,
                role_id="global-role",
            )

        assert policies.has_global_role(
            user_id=retained,
            role_id="retained-role",
        )

    def test_clear_assignments_for_identities__empty_list_does_nothing(
        self,
        policies: CasbinPolicies,
    ):
        assert not policies.clear_assignments_for_identities(identity_ids=[])

    def test_clear_assignments_for_identities__removes_policy_from_another_worker(
        self, policies: CasbinPolicies
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
        assert not policies.has_resource_role(
            user_id=user,
            role_id=role,
            resource_id=resource,
        )

        updated = policies.clear_assignments_for_identities(identity_ids=[user])

        assert updated
        assert not policies.has_resource_role(
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
    def test_auto_reload_resolves_stale_policy(self, policies: CasbinPolicies):
        """Regression test: a role assigned by another worker (direct DB write) is
        invisible until the enforcer reloads and the TTL cache expires."""
        role = "staleness_role"
        user = "staleness_user"
        resource = "staleness_resource"
        action = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        policies.sync_role_permissions(role_id=role, actions=[action])
        assert policies.allows(sub=user, dom="*", obj=resource, act=action) is False

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
        assert policies.allows(sub=user, dom="*", obj=resource, act=action) is False

        # Simulate start_auto_load_policy firing and the TTL cache expiring
        policies._enforcer.load_policy()
        policies._cache.clear()

        # Access is now correctly granted
        assert policies.allows(sub=user, dom="*", obj=resource, act=action) is True

        # Cleanup
        with engine.begin() as conn:
            conn.execute(
                text(
                    "DELETE FROM casbin_rule "
                    "WHERE ptype='g' AND v0=:u AND v1=:r AND v2=:obj"
                ),
                {"u": user, "r": role, "obj": resource},
            )
        policies.remove_role_permissions(role_id=role)


class TestReplaceAll:
    def test_replace_all__changes_nothing_when_in_sync(self, policies: CasbinPolicies):
        rules: set[Rule] = {
            Permission("role", AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES),
            ResourceRole("user", "role", "resource"),
            *membership_rules("user", "group"),
        }

        policies.replace_all(rules)
        policies._enforcer.load_policy()

        assert policies.replace_all(rules) == (0, 0)

    def test_replace_all__keeps_the_table_state_when_saving_fails(
        self, policies: CasbinPolicies, monkeypatch
    ):
        action = AuthorizationAction.GLOBAL__CREATE_USER
        permission = Permission("group", action)
        policies.replace_all({permission, GlobalRole("member", "group")})

        def fail() -> None:
            raise RuntimeError("database unavailable")

        monkeypatch.setattr(policies._enforcer, "save_policy", fail)
        with pytest.raises(RuntimeError):
            policies.replace_all({permission})

        assert policies.allows(sub="member", dom="*", obj="*", act=action)

    def test_replace_all__removes_duplicate_and_unloaded_rows(
        self, policies: CasbinPolicies
    ):
        kept = ("member", "group")
        stale = ("member", "other-group")
        self._insert_global_roles(kept, kept, stale, stale)
        policies._enforcer.load_policy()
        self._insert_global_roles(("member", "unloaded-group"))
        policies.replace_all({GlobalRole("member", "group")})

        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT v1 FROM casbin_rule WHERE ptype='g3' AND v0='member'")
            ).all()
        assert [row.v1 for row in rows] == ["group"]

    @staticmethod
    def _insert_global_roles(*rows: tuple[str, str]) -> None:
        with engine.begin() as conn:
            for member, group in rows:
                conn.execute(
                    text(
                        "INSERT INTO casbin_rule (ptype, v0, v1) VALUES ('g3', :m, :g)"
                    ),
                    {"m": member, "g": group},
                )
