from casbin_sqlalchemy_adapter import CasbinRule

from app.authorization.service import AuthorizationService
from app.core.authz import Authorization
from app.database.database import get_db_session


class TestAuthorizationService:

    def test_clear_casbin_table(self, authorizer: Authorization, enable_authorizer):
        db = next(get_db_session())

        existing = len(db.query(CasbinRule).all())

        for i in range(5):
            authorizer.assign_resource_role(
                user_id="test", role_id="test", resource_id=f"test_{i}"
            )

        assert len(db.query(CasbinRule).all()) == 5 + existing, "roles not recorded"

        service = AuthorizationService(db=db)
        service._clear_casbin_table()

        assert len(db.query(CasbinRule).all()) == 0, "database not cleared"
