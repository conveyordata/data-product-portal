from contextlib import contextmanager

import pytest
from fastapi import HTTPException

from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization


@contextmanager
def not_raises(exception):
    try:
        yield
    except exception:
        raise pytest.fail("DID RAISE {0}".format(exception))


@pytest.fixture(scope="module", autouse=True)
async def authorizer():
    authorization = await Authorization.initialize()
    yield authorization


class TestAuthorization:

    @pytest.mark.asyncio(loop_scope="module")
    async def test_everyone_role(self, authorizer: Authorization):
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        await authorizer.sync_everyone_role(actions=[allowed])

        with not_raises(HTTPException):
            authorizer._enforce(
                sub="does_not_matter",
                dom="does_not_matter",
                obj="does_not_matter",
                act=allowed,
            )

        with pytest.raises(HTTPException):
            authorizer._enforce(
                sub="does_not_matter",
                dom="does_not_matter",
                obj="does_not_matter",
                act=denied,
            )

        # Clear role definition again
        await authorizer.sync_everyone_role(actions=[])

        with pytest.raises(HTTPException):
            authorizer._enforce(
                sub="does_not_matter",
                dom="does_not_matter",
                obj="does_not_matter",
                act=allowed,
            )

    @pytest.mark.asyncio(loop_scope="module")
    async def test_resource_role(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        await authorizer.sync_role(role_id=role, actions=[allowed])
        await authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        with not_raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=allowed)

        with pytest.raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=denied)

        with pytest.raises(HTTPException):
            authorizer._enforce(
                sub=user, dom="does_not_matter", obj="other_resource", act=allowed
            )

        # Clear role assignment again
        await authorizer.revoke_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        with pytest.raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=allowed)

    @pytest.mark.asyncio(loop_scope="module")
    async def test_domain_role(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        dom = "test_domain"
        allowed = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES
        denied = AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS

        await authorizer.sync_role(role_id=role, actions=[allowed])
        await authorizer.assign_domain_role(user_id=user, role_id=role, domain_id=dom)

        with not_raises(HTTPException):
            authorizer._enforce(sub=user, dom=dom, obj="does_not_matter", act=allowed)

        with pytest.raises(HTTPException):
            authorizer._enforce(sub=user, dom=dom, obj="does_not_matter", act=denied)

        with pytest.raises(HTTPException):
            authorizer._enforce(
                sub=user, dom="other_dom", obj="does_not_matter", act=allowed
            )

        # Clear role assignment again
        await authorizer.revoke_domain_role(user_id=user, role_id=role, domain_id=dom)

        with pytest.raises(HTTPException):
            authorizer._enforce(sub=user, dom=dom, obj="does_not_matter", act=allowed)

    @pytest.mark.asyncio(loop_scope="module")
    async def test_admin_role(self, authorizer: Authorization):
        user = "test_user"

        with pytest.raises(HTTPException):
            authorizer._enforce(
                sub=user, dom="does_not_matter", obj="does_not_matter", act=0
            )

        await authorizer.assign_admin_role(user_id=user)

        with not_raises(HTTPException):
            authorizer._enforce(
                sub=user, dom="does_not_matter", obj="does_not_matter", act=0
            )

        await authorizer.revoke_admin_role(user_id=user)

        with pytest.raises(HTTPException):
            authorizer._enforce(
                sub=user, dom="does_not_matter", obj="does_not_matter", act=0
            )

    @pytest.mark.asyncio(loop_scope="module")
    async def test_role_removal(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES

        await authorizer.sync_role(role_id=role, actions=[act])
        await authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        with not_raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=act)

        # Clear role assignment again
        await authorizer.remove_role(role_id=role)

        with pytest.raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=act)

    @pytest.mark.asyncio(loop_scope="module")
    async def test_multiple_permissions(self, authorizer: Authorization):
        role = "test_role"
        user = "test_user"
        obj = "test_resource"
        act = AuthorizationAction.DATA_PRODUCT__DELETE
        all_acts = list(map(lambda a: a, AuthorizationAction))

        await authorizer.sync_role(role_id=role, actions=all_acts)
        await authorizer.assign_resource_role(
            user_id=user, role_id=role, resource_id=obj
        )

        with not_raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=act)

        await authorizer.remove_role(role_id=role)

        with pytest.raises(HTTPException):
            authorizer._enforce(sub=user, dom="does_not_matter", obj=obj, act=act)
