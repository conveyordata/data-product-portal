from tests.factories import (
    DataProductFactory,
    DataProductMembershipFactory,
    UserFactory,
)

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)

MEMBERSHIPS_ENDPOINT = "/api/data_product_memberships"


class TestDataProductMembershipsRouter:
    def test_create_data_product_membership(self, client):
        membership = DataProductMembershipFactory(user=UserFactory(external_id="sub"))
        new_user = UserFactory()

        response = self.create_secondary_membership(
            client, new_user.id, membership.data_product_id
        )
        assert response.status_code == 200

    def test_create_data_product_membership_by_admin(self, client, admin):
        membership = DataProductMembershipFactory(role=DataProductUserRole.MEMBER.value)
        new_user = UserFactory()
        response = self.create_secondary_membership(
            client, new_user.id, membership.data_product_id
        )
        assert response.status_code == 200

    def test_request_data_product_membership(self, client):
        data_product = DataProductFactory()
        user = UserFactory()

        response = self.request_data_product_membership(
            client, user.id, data_product.id
        )
        assert response.status_code == 200

    def test_approve_data_product_membership_request(self, client):
        owner_membership = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        )
        user = UserFactory()
        membership_request = DataProductMembershipFactory(
            data_product=owner_membership.data_product,
            user=user,
            role=DataProductUserRole.MEMBER.value,
            status=DataProductMembershipStatus.PENDING_APPROVAL.value,
            requested_by_id=str(user.id),
        )

        response = self.approve_data_product_membership(client, membership_request.id)
        assert response.status_code == 200

    def test_deny_data_product_membership_request(self, client):
        owner_membership = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        )
        user = UserFactory()
        membership_request = DataProductMembershipFactory(
            data_product=owner_membership.data_product,
            user=user,
            role=DataProductUserRole.MEMBER.value,
            status=DataProductMembershipStatus.PENDING_APPROVAL.value,
            requested_by_id=str(user.id),
        )

        response = self.deny_data_product_membership(client, membership_request.id)
        assert response.status_code == 200

    def test_remove_data_product_membership(self, client):
        membership_1 = DataProductMembershipFactory(user=UserFactory(external_id="sub"))
        membership_2 = DataProductMembershipFactory(
            data_product=membership_1.data_product
        )

        response = self.remove_data_product_membership(client, membership_2.id)
        assert response.status_code == 200

    def test_update_data_product_membership_role(self, client):
        owner_membership = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        )
        membership = DataProductMembershipFactory(
            data_product=owner_membership.data_product,
            user=UserFactory(),
            role=DataProductUserRole.MEMBER.value,
        )

        response = self.update_data_product_membership_user_role(
            client, membership.id, DataProductUserRole.OWNER.value
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
        assert response.json()[0]["status"] == "pending_approval"

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

    @staticmethod
    def approve_data_product_membership(client, membership_id):
        return client.post(f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/approve")

    @staticmethod
    def deny_data_product_membership(client, membership_id):
        return client.post(f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/deny")

    @staticmethod
    def remove_data_product_membership(client, membership_id):
        return client.post(f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/remove")

    @staticmethod
    def update_data_product_membership_user_role(client, membership_id, new_role):
        return client.put(
            f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/role?membership_role={new_role}"
        )
