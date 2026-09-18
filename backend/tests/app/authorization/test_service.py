from casbin_sqlalchemy_adapter import CasbinRule

from app.authorization.service import AuthorizationService
from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from tests.factories.group import GroupFactory, GroupMembershipFactory


class TestAuthorizationService:
    def test_reload_enforcer(self, authorizer: Authorization, session):
        existing = len(session.query(CasbinRule).all())

        for i in range(5):
            authorizer.assign_resource_role(
                user_id="test", role_id="test", resource_id=f"test_{i}"
            )

        assert len(session.query(CasbinRule).all()) == 5 + existing, (
            "roles not recorded"
        )

        service = AuthorizationService(session)
        service.reload_enforcer()

        assert len(session.query(CasbinRule).all()) == existing, (
            "Syncing did not remove the roles"
        )

    def test_reload_enforcer_ensure_discoverable_data_products_sync(
        self, authorizer: Authorization, session
    ):
        existing = len(session.query(CasbinRule).all())

        for i in range(5):
            DataProductFactory(visibility=DataProductVisibility.DISCOVERABLE)
            DataProductFactory(visibility=DataProductVisibility.HIDDEN)

        assert len(session.query(CasbinRule).all()) == 5 + existing, (
            "roles not recorded"
        )

        service = AuthorizationService(session)
        service.reload_enforcer()

        assert len(session.query(CasbinRule).all()) == 5 + existing, (
            "database not cleared"
        )

    def test_reload_enforcer_syncs_group_data_product_access(
        self, authorizer: Authorization, session
    ):
        user = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)

        data_product = DataProductFactory()
        role = RoleFactory(
            scope="data_product",
            permissions=[AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            identity=group,
            data_product=data_product,
            role=role,
        )

        AuthorizationService(session).reload_enforcer()

        assert authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        )

    def test_reload_enforcer_syncs_group_global_access(
        self, authorizer: Authorization, session
    ):
        user = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)

        action = AuthorizationAction.DATA_PRODUCT__DELETE
        role = RoleFactory(
            scope="global",
            permissions=[action],
        )
        GlobalRoleAssignmentFactory(
            identity=group,
            role=role,
        )

        AuthorizationService(session).reload_enforcer()

        assert authorizer.has_access(
            sub=str(user.id),
            dom="*",
            obj="*",
            act=action,
        )

    def test_reload_enforcer_revokes_access_after_membership_removal(
        self, authorizer: Authorization, session
    ):
        """
        This test ensures that the authorization service properly revokes access to a user after their membership is removed.
        The access is removed calling `self._enforcer.build_role_links()` in `start_enforcer_after_reload()`.
        """
        user = UserFactory()
        group = GroupFactory()
        membership = GroupMembershipFactory(group=group, member=user)

        data_product = DataProductFactory()
        role = RoleFactory(
            scope="data_product",
            permissions=[AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            identity=group,
            data_product=data_product,
            role=role,
        )

        service = AuthorizationService(session)
        service.reload_enforcer()

        assert authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        )

        session.delete(membership)
        session.commit()
        service.reload_enforcer()

        assert not authorizer.has_access(
            sub=str(user.id),
            dom=str(data_product.domain_id),
            obj=str(data_product.id),
            act=AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        )
