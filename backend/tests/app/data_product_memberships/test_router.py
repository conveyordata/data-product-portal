from tests.factories import (
    DataProductFactory,
    DataProductMembershipFactory,
    UserFactory,
)

from app.data_product_memberships.enums import (
    DataProductUserRole,
)

MEMBERSHIPS_ENDPOINT = "/api/data_product_memberships"


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

    @staticmethod
    def create_secondary_membership(client, user_id, data_product_id):
        data = {
            "role": DataProductUserRole.MEMBER.value,
            "user_id": str(user_id),
        }
        return client.post(
            f"{MEMBERSHIPS_ENDPOINT}/create?data_product_id={str(data_product_id)}",
            json=data,
        )

    @staticmethod
    def request_data_product_membership(client, user_id, data_product_id):
        return client.post(
            f"{MEMBERSHIPS_ENDPOINT}/request?user_id={str(user_id)}"
            f"&data_product_id={str(data_product_id)}"
        )
