from casbin_sqlalchemy_adapter import CasbinRule

from app.authorization.service import AuthorizationService
from app.core.authz import Authorization
from app.data_products.model import DataProductVisibility
from tests.factories import DataProductFactory


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
        self,
        authorizer: Authorization,
        session,
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
