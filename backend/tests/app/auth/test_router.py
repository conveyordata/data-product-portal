from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    EnvironmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz.actions import AuthorizationAction
from app.roles.schema import Scope

ENDPOINT = "/api/auth"


class TestAuthRouter:
    def test_authorize_user(self, client):
        response = client.get(f"{ENDPOINT}/user")
        assert response.status_code == 200
        assert response.json()["external_id"] == "sub"

    def test_aws_credentials(self, client):
        EnvironmentFactory(name="production")
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = client.get(
            f"{ENDPOINT}/aws_credentials?data_product_name"
            f"={data_product.namespace}"
            "&environment=production"
        )
        assert (
            response.status_code == 501 or response.status_code == 400
        )  # TODO Actually test through mocking
