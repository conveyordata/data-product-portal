from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.environment import EnvironmentFactory
from tests.factories.user import UserFactory

ENDPOINT = "/api/auth"


class TestAuthRouter:
    def test_authorize_user(self, client):
        response = client.get(f"{ENDPOINT}/user")
        assert response.status_code == 200
        assert response.json()["external_id"] == "sub"

    def test_aws_credentials(self, client):
        EnvironmentFactory(name="production")
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = client.get(
            f"{ENDPOINT}/aws_credentials?data_product_name"
            f"={data_product.external_id}"
            "&environment=production"
        )
        assert (
            response.status_code == 501 or response.status_code == 400
        )  # TODO Actually test through mocking
