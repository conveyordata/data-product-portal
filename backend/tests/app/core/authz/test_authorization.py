from typing import cast

import pytest

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization

ANY: str = "does_not_matter"
ANY_ACT: AuthorizationAction = cast(AuthorizationAction, 0)


class TestAuthorization:

    @pytest.mark.asyncio(loop_scope="session")
    async def test_everyone_role(self, authorizer: Authorization):
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        await authorizer.sync_everyone_role_permissions(actions=[allowed])

        assert authorizer.has_access(sub=ANY, dom=ANY, obj=ANY, act=allowed) is True
        assert authorizer.has_access(sub=ANY, dom=ANY, obj=ANY, act=denied) is False

        # Clear role definition again
        await authorizer.sync_everyone_role_permissions(actions=[])
        assert authorizer.has_access(sub=ANY, dom=ANY, obj=ANY, act=allowed) is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_resource_role(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        await authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        await authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=allowed) is True
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=denied) is False
        assert (
            authorizer.has_access(sub=user, dom=ANY, obj="other_resource", act=denied)
            is False
        )

        # Clear role assignment again
        await authorizer.revoke_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=allowed) is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_domain_role(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        dom = "test_domain"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        await authorizer.sync_role_permissions(role_id=role, actions=[allowed])
        await authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom)

        assert authorizer.has_access(sub=user, dom=dom, obj=ANY, act=allowed) is True
        assert authorizer.has_access(sub=user, dom=dom, obj=ANY, act=denied) is False
        assert (
            authorizer.has_access(sub=user, dom="other_dom", obj=ANY, act=allowed)
            is False
        )

        # Clear role assignment again
        await authorizer.revoke_domain_role(user_id=user, role_id=role, domain_id=dom)
        assert authorizer.has_access(sub=user, dom=dom, obj=ANY, act=allowed) is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_admin_role(self, authorizer: Authorization):
        user = "test_user"

        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

        await authorizer.assign_admin_role(user_id=user)
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is True

        await authorizer.revoke_admin_role(user_id=user)
        assert authorizer.has_access(sub=user, dom=ANY, obj=ANY, act=ANY_ACT) is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_role_removal(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        await authorizer.sync_role_permissions(role_id=role, actions=[act])
        await authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is True

        # Clear role assignment again
        await authorizer.remove_role_permissions(role_id=role)
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_multiple_permissions(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE
        all_acts = list(map(lambda a: a, AuthorizationAction))

        await authorizer.sync_role_permissions(role_id=role, actions=all_acts)
        await authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is True

        await authorizer.remove_role_permissions(role_id=role)
        assert authorizer.has_access(sub=user, dom=ANY, obj=obj, act=act) is False
