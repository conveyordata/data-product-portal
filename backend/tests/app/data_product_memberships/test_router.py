from tests.factories import (
    DataProductFactory,
    DataProductMembershipFactory,
    UserFactory,
)

from app.data_product_memberships.enums import (
    DataProductUserRole,
)

MEMBERSHIPS_ENDPOINT = "/api/data_product_memberships"
DATA_PRODUCTS_ENDPOINT = "/api/data_products"


class TestDataProductMembershipsRouter:
    def test_request_data_product_membership(self, client):
        data_product = DataProductFactory()
        user = UserFactory()

        response = self.request_data_product_membership(
            client, user.id, data_product.id
        )
        assert response.status_code == 200

    def test_get_pending_actions_no_action(self, client):
        DataProductMembershipFactory(user=UserFactory(external_id="sub"))
        response = client.get(f"{MEMBERSHIPS_ENDPOINT}/actions")
        assert response.json() == []

    def test_get_pending_actions(self, client):
        owner_membership = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        )
        self.request_data_product_membership(
            client, UserFactory().id, owner_membership.data_product.id
        )
        response = client.get(f"{MEMBERSHIPS_ENDPOINT}/actions")
        assert response.json()[0]["data_product_id"] == str(
            owner_membership.data_product.id
        )
        assert response.json()[0]["status"] == "pending"

    def test_data_product_membership_history(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(
            role=DataProductUserRole.OWNER.value, user=user
        ).data_product
        link_requested = self.request_data_product_membership(
            client, UserFactory().id, data_product.id
        )
        link_id = link_requested.json().get("id")
        assert link_id is not None
        response = self.get_data_product_history(client, data_product.id)
        assert len(response.json()) == 1

    @staticmethod
    def request_data_product_membership(client, user_id, data_product_id):
        return client.post(
            f"{MEMBERSHIPS_ENDPOINT}/request?user_id={str(user_id)}"
            f"&data_product_id={str(data_product_id)}"
        )

    @staticmethod
    def get_data_product_history(client, data_product_id):
        return client.get(f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/history")
