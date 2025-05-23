from typing import cast

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization

ANY: str = "does_not_matter"
ANY_ACT: AuthorizationAction = cast(AuthorizationAction, 0)


class TestAuthorization:

    def test_everyone_role(self, authorizer: Authorization):
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_everyone_role_permissions(actions=[allowed])

        assert authorizer.has_access(sub=ANY, dom=ANY, obj=ANY, act=allowed) is True
        assert authorizer.has_access(sub=ANY, dom=ANY, obj=ANY, act=denied) is False

        # Clear role definition again
        authorizer.sync_everyone_role_permissions(actions=[])
        assert authorizer.has_access(sub=ANY, dom=ANY, obj=ANY, act=allowed) is False

    def test_resource_role(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=allowed) is True
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=denied) is False
        assert (
            authorizer.has_access(sub=user, dom=ANY, obj="other_resource", act=denied)
            is False
        )

        # Clear role assignment again
        authorizer.revoke_resource_role(user_id=user, role_id=role, resource_id=obj)
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=allowed) is False

    def test_domain_role(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        dom = "test_domain"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom)

        assert authorizer.has_access(sub=user, dom=dom, obj=ANY, act=allowed) is True
        assert authorizer.has_access(sub=user, dom=dom, obj=ANY, act=denied) is False
        assert (
            authorizer.has_access(sub=user, dom="other_dom", obj=ANY, act=allowed)
            is False
        )

        # Clear role assignment again
        authorizer.revoke_domain_role(user_id=user, role_id=role, domain_id=dom)
        assert authorizer.has_access(sub=user, dom=dom, obj=ANY, act=allowed) is False

    def test_global_role(self, authorizer: Authorization):
        user = "test_user"
        role = "test_role"
        act = AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=act) is False

        authorizer.assign_global_role(user_id=user, role_id=role)
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=act) is True

        authorizer.revoke_global_role(user_id=user, role_id=role)
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=act) is False

    def test_admin_role(self, authorizer: Authorization):
        user = "test_user"

        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

        authorizer.assign_admin_role(user_id=user)
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is True

        authorizer.revoke_admin_role(user_id=user)
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

    def test_role_removal(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is True

        # Clear role assignment again
        authorizer.remove_role_permissions(role_id=role)
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is False

    def test_multiple_permissions(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE
        all_acts = list(map(lambda a: a, AuthorizationAction))

        authorizer.sync_role_permissions(role_id=role, actions=all_acts)
        authorizer.assign_resource_role(user_id=user, role_id=role, resource_id=obj)

        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is True

        authorizer.remove_role_permissions(role_id=role)
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is False

    def test_clear_assignments_for_resource_role(self, authorizer: Authorization):
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

    def test_clear_assignments_for_domain_role(self, authorizer: Authorization):
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

    def test_clear_assignments_for_global_role(self, authorizer: Authorization):
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

    def test_clear_assignments_for_user(self, authorizer: Authorization):
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

    def test_clear_assignments_for_resource(self, authorizer: Authorization):
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

    def test_clear_assignments_for_domain(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        dom1 = "test_domain"
        dom2 = "other_domain"
        act = AuthorizationAction.DATA_PRODUCT__DELETE

        authorizer.sync_role_permissions(role_id=role, actions=[act])
        authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom1)
        authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom2)
        assert authorizer.has_domain_role(user_id=user, role_id=role, domain_id=dom1)
        assert authorizer.has_domain_role(user_id=user, role_id=role, domain_id=dom2)

        authorizer.clear_assignments_for_domain(domain_id=dom1)
        assert not authorizer.has_domain_role(
            user_id=user, role_id=role, domain_id=dom1
        )
        assert authorizer.has_domain_role(user_id=user, role_id=role, domain_id=dom2)
