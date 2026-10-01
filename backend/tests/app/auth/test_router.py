from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    EnvironmentFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/authn"
CURRENT_USER_ENDPOINT = "/api/v2/users/current"


class TestAuthRouter:
    def test_authorize_user(self, client):
        response = client.get(f"{CURRENT_USER_ENDPOINT}")
        assert response.status_code == 200
        assert response.json()["external_id"] == settings.DEFAULT_USERNAME

    def test_authorize_user__accepts_an_email_without_a_dot_before_the_at(self, client):
        response = client.get(
            CURRENT_USER_ENDPOINT, headers={"X-User": "jane@pharma.com"}
        )
        assert response.status_code == 200
        assert response.json()["first_name"] == "jane"
        assert response.json()["last_name"] == ""

    def test_aws_credentials(self, client):
        EnvironmentFactory(name="production")
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = client.get(
            f"{ENDPOINT}/aws_credentials?data_product_name"
            f"={data_product.namespace}"
            "&environment=production"
        )
        assert response.status_code == 501 or response.status_code == 400
