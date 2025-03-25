from tests.factories import (
    DataProductMembershipFactory,
    DatasetFactory,
    UserFactory,
)
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_output_dataset_notification import (
    DataOutputDatasetNotificationFactory,
)
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory
from tests.factories.data_product_dataset_notification import (
    DataProductDatasetNotificationFactory,
)
from tests.factories.data_product_membership_notification import (
    DataProductMembershipNotificationFactory,
)
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory
from tests.factories.notification_interaction import NotificationInteractionFactory

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.datasets.enums import DatasetAccessType

NOTIFICATIONS_ENDPOINT = "/api/notifications"
DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/data_product_dataset_links"
DATA_PRODUCTS_ENDPOINT = "/api/data_products"
DATA_OUTPUTS_ENDPOINT = "/api/data_outputs"
MEMBERSHIPS_ENDPOINT = "/api/data_product_memberships"
DATASET_ENDPOINT = "/api/datasets"
DATA_OUTPUTS_DATASETS_ENDPOINT = "/api/data_output_dataset_links"


class TestNotificationsRouter:

    def test_get_pending_actions_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub")
        membership = DataProductMembershipFactory(user=owner)
        ds = DatasetFactory(owners=[owner], access_type=DatasetAccessType.RESTRICTED)

        response = self.request_data_product_dataset_link(
            client, membership.data_product_id, ds.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataProductDataset"
        )
        assert response.json()[0]["notification"]["data_product_dataset"][
            "data_product_id"
        ] == str(membership.data_product.id)
        assert (
            response.json()[0]["notification"]["data_product_dataset"]["status"]
            == "pending_approval"
        )
        assert response.json()[0]["notification"]["data_product_dataset"][
            "requested_by"
        ]["id"] == str(owner.id)

        all_notifications = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == all_notifications.json()

    def test_get_pending_actions_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        membership = DataProductMembershipFactory(user=owner)
        data_output = DataOutputFactory(owner=membership.data_product)
        ds = DatasetFactory(owners=[owner])

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataOutputDataset"
        )
        assert response.json()[0]["notification"]["data_output_dataset"][
            "data_output_id"
        ] == str(data_output.id)
        assert (
            response.json()[0]["notification"]["data_output_dataset"]["status"]
            == "pending_approval"
        )
        assert response.json()[0]["notification"]["data_output_dataset"][
            "requested_by"
        ]["id"] == str(owner.id)

        all_notifications = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == all_notifications.json()

    def test_get_pending_actions_data_product_membership(self, client):
        owner_membership = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        )
        user_id = UserFactory().id
        response = self.request_data_product_membership(
            client, user_id, owner_membership.data_product.id
        )
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataProductMembership"
        )
        assert response.json()[0]["notification"]["data_product_membership"][
            "data_product_id"
        ] == str(owner_membership.data_product.id)
        assert (
            response.json()[0]["notification"]["data_product_membership"]["status"]
            == "pending_approval"
        )
        assert response.json()[0]["notification"]["data_product_membership"]["user"][
            "id"
        ] == str(user_id)

        all_notifications = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == all_notifications.json()

    def test_change_notification_ownership_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        membership = DataProductMembershipFactory(user=owner)
        ds = DatasetFactory(
            owners=[owner, UserFactory()], access_type=DatasetAccessType.RESTRICTED
        )

        response = self.request_data_product_dataset_link(
            client, membership.data_product_id, ds.id
        )
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json()[0]["notification"]["data_product_dataset"][
            "data_product_id"
        ] == str(membership.data_product.id)

        response = self.delete_dataset_user(client, owner.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json() == []

        response = self.add_user_to_dataset(client, owner.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json()[0]["notification"]["data_product_dataset"][
            "data_product_id"
        ] == str(membership.data_product.id)

    def test_change_notification_ownership_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        membership = DataProductMembershipFactory(user=owner)
        data_output = DataOutputFactory(owner=membership.data_product)
        ds = DatasetFactory(owners=[owner, UserFactory()])

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json()[0]["notification"]["data_output_dataset"][
            "data_output_id"
        ] == str(data_output.id)

        response = self.delete_dataset_user(client, owner.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json() == []

        response = self.add_user_to_dataset(client, owner.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json()[0]["notification"]["data_output_dataset"][
            "data_output_id"
        ] == str(data_output.id)

    def test_change_notification_ownership_data_product_membership(self, client):
        owner_membership = DataProductMembershipFactory(
            user=UserFactory(external_id="sub", is_admin=True)
        )
        DataProductMembershipFactory(
            data_product=owner_membership.data_product, user=UserFactory()
        )

        response = self.request_data_product_membership(
            client, UserFactory().id, owner_membership.data_product.id
        )
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json()[0]["notification"]["data_product_membership"][
            "data_product_id"
        ] == str(owner_membership.data_product.id)

        response = self.remove_data_product_membership(client, owner_membership.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json() == []

        response = self.create_data_product_owner_membership(
            client, owner_membership.user.id, owner_membership.data_product.id
        )
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}/actions")
        assert response.json()[0]["notification"]["data_product_membership"][
            "data_product_id"
        ] == str(owner_membership.data_product.id)

    def test_approve_data_product_dataset(self, client):
        requester = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[requester])
        link = DataProductDatasetAssociationFactory(
            dataset=ds,
            status=DataProductDatasetLinkStatus.PENDING_APPROVAL.value,
            requested_by=requester,
        )
        NotificationInteractionFactory(
            notification=DataProductDatasetNotificationFactory(
                data_product_dataset=link
            ),
            user=requester,
        )
        response = self.approve_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataProductDataset"
        )
        assert response.json()[0]["notification"]["data_product_dataset"]["id"] == str(
            link.id
        )
        assert (
            response.json()[0]["notification"]["data_product_dataset"]["status"]
            == "approved"
        )
        assert response.json()[0]["notification"]["data_product_dataset"][
            "requested_by"
        ]["id"] == str(requester.id)

    def test_deny_data_product_dataset(self, client):
        requester = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[requester])
        link = DataProductDatasetAssociationFactory(
            dataset=ds,
            status=DataProductDatasetLinkStatus.PENDING_APPROVAL.value,
            requested_by=requester,
        )
        NotificationInteractionFactory(
            notification=DataProductDatasetNotificationFactory(
                data_product_dataset=link
            ),
            user=requester,
        )
        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataProductDataset"
        )
        assert response.json()[0]["notification"]["data_product_dataset"]["id"] == str(
            link.id
        )
        assert (
            response.json()[0]["notification"]["data_product_dataset"]["status"]
            == "denied"
        )
        assert response.json()[0]["notification"]["data_product_dataset"][
            "requested_by"
        ]["id"] == str(requester.id)

    def test_approve_data_output_dataset(self, client):
        requester = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[requester])
        link = DataOutputDatasetAssociationFactory(
            dataset=ds,
            status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value,
            requested_by=requester,
        )
        NotificationInteractionFactory(
            notification=DataOutputDatasetNotificationFactory(data_output_dataset=link),
            user=requester,
        )
        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataOutputDataset"
        )
        assert response.json()[0]["notification"]["data_output_dataset"]["id"] == str(
            link.id
        )
        assert (
            response.json()[0]["notification"]["data_output_dataset"]["status"]
            == "approved"
        )
        assert response.json()[0]["notification"]["data_output_dataset"][
            "requested_by"
        ]["id"] == str(requester.id)

    def test_deny_data_output_dataset(self, client):
        requester = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[requester])
        link = DataOutputDatasetAssociationFactory(
            dataset=ds,
            status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value,
            requested_by=requester,
        )
        NotificationInteractionFactory(
            notification=DataOutputDatasetNotificationFactory(data_output_dataset=link),
            user=requester,
        )
        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataOutputDataset"
        )
        assert response.json()[0]["notification"]["data_output_dataset"]["id"] == str(
            link.id
        )
        assert (
            response.json()[0]["notification"]["data_output_dataset"]["status"]
            == "denied"
        )
        assert response.json()[0]["notification"]["data_output_dataset"][
            "requested_by"
        ]["id"] == str(requester.id)

    def test_approve_data_product_membership(self, client):
        requester = UserFactory(external_id="sub")
        owner_membership = DataProductMembershipFactory(user=requester)
        membership_request = DataProductMembershipFactory(
            data_product=owner_membership.data_product,
            user=requester,
            role=DataProductUserRole.MEMBER.value,
            status=DataProductMembershipStatus.PENDING_APPROVAL.value,
            requested_by_id=str(requester.id),
        )
        NotificationInteractionFactory(
            notification=DataProductMembershipNotificationFactory(
                data_product_membership=membership_request
            ),
            user=requester,
        )
        response = self.approve_data_product_membership(client, membership_request.id)
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataProductMembership"
        )
        assert response.json()[0]["notification"]["data_product_membership"][
            "id"
        ] == str(membership_request.id)
        assert (
            response.json()[0]["notification"]["data_product_membership"]["status"]
            == "approved"
        )
        assert response.json()[0]["notification"]["data_product_membership"]["user"][
            "id"
        ] == str(requester.id)

    def test_deny_data_product_membership(self, client):
        requester = UserFactory(external_id="sub")
        owner_membership = DataProductMembershipFactory(user=requester)
        membership_request = DataProductMembershipFactory(
            data_product=owner_membership.data_product,
            user=requester,
            role=DataProductUserRole.MEMBER.value,
            status=DataProductMembershipStatus.PENDING_APPROVAL.value,
            requested_by_id=str(requester.id),
        )
        NotificationInteractionFactory(
            notification=DataProductMembershipNotificationFactory(
                data_product_membership=membership_request
            ),
            user=requester,
        )
        response = self.deny_data_product_membership(client, membership_request.id)
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification"]["configuration_type"]
            == "DataProductMembership"
        )
        assert response.json()[0]["notification"]["data_product_membership"][
            "id"
        ] == str(membership_request.id)
        assert (
            response.json()[0]["notification"]["data_product_membership"]["status"]
            == "denied"
        )
        assert response.json()[0]["notification"]["data_product_membership"]["user"][
            "id"
        ] == str(requester.id)

    def test_delete_parent_dataset_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[owner])
        link = DataProductDatasetAssociationFactory(
            dataset=ds,
            status=DataProductDatasetLinkStatus.PENDING_APPROVAL.value,
        )
        NotificationInteractionFactory(
            notification=DataProductDatasetNotificationFactory(
                data_product_dataset=link
            ),
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["notification"]["data_product_dataset"]["id"] == str(
            link.id
        )
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_dataset_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[owner])
        link = DataOutputDatasetAssociationFactory(
            dataset=ds,
            status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value,
        )
        NotificationInteractionFactory(
            notification=DataOutputDatasetNotificationFactory(data_output_dataset=link),
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["notification"]["data_output_dataset"]["id"] == str(
            link.id
        )
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_product_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataProductDatasetAssociationFactory(
            status=DataProductDatasetLinkStatus.PENDING_APPROVAL.value,
            data_product=(DataProductMembershipFactory(user=owner).data_product),
        )
        NotificationInteractionFactory(
            notification=DataProductDatasetNotificationFactory(
                data_product_dataset=link
            ),
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["notification"]["data_product_dataset"]["id"] == str(
            link.id
        )
        response = self.delete_data_product(client, link.data_product.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_product_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataOutputDatasetAssociationFactory(
            status=DataProductDatasetLinkStatus.PENDING_APPROVAL.value,
            data_output=DataOutputFactory(
                owner=(DataProductMembershipFactory(user=owner).data_product)
            ),
        )
        NotificationInteractionFactory(
            notification=DataOutputDatasetNotificationFactory(data_output_dataset=link),
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["notification"]["data_output_dataset"]["id"] == str(
            link.id
        )
        response = self.delete_data_product(client, link.data_output.owner.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_product_data_product_membership(self, client):
        owner = UserFactory(external_id="sub")
        membership = DataProductMembershipFactory(
            status=DataProductMembershipStatus.PENDING_APPROVAL.value,
            data_product=(DataProductMembershipFactory(user=owner).data_product),
        )
        NotificationInteractionFactory(
            notification=DataProductMembershipNotificationFactory(
                data_product_membership=membership
            ),
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["notification"]["data_product_membership"][
            "id"
        ] == str(membership.id)
        response = self.delete_data_product(client, membership.data_product.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_output_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataOutputDatasetAssociationFactory(
            status=DataProductDatasetLinkStatus.PENDING_APPROVAL.value,
            data_output=DataOutputFactory(
                owner=(DataProductMembershipFactory(user=owner).data_product)
            ),
        )
        NotificationInteractionFactory(
            notification=DataOutputDatasetNotificationFactory(data_output_dataset=link),
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["notification"]["data_output_dataset"]["id"] == str(
            link.id
        )
        response = self.delete_data_output(client, link.data_output.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    @staticmethod
    def request_data_product_dataset_link(client, data_product_id, dataset_id):
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def request_data_output_dataset_link(client, data_output_id, dataset_id):
        return client.post(
            f"{DATA_OUTPUTS_ENDPOINT}/{data_output_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def request_data_product_membership(client, user_id, data_product_id):
        return client.post(
            f"{MEMBERSHIPS_ENDPOINT}/request?user_id={str(user_id)}"
            f"&data_product_id={str(data_product_id)}"
        )

    @staticmethod
    def delete_dataset_user(client, user_id, dataset_id):
        return client.delete(f"{DATASET_ENDPOINT}/{dataset_id}/user/{user_id}")

    @staticmethod
    def add_user_to_dataset(client, user_id, dataset_id):
        return client.post(f"{DATASET_ENDPOINT}/{dataset_id}/user/{user_id}")

    @staticmethod
    def remove_data_product_membership(client, membership_id):
        return client.post(f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/remove")

    @staticmethod
    def create_data_product_owner_membership(client, user_id, data_product_id):
        data = {
            "role": DataProductUserRole.OWNER.value,
            "user_id": str(user_id),
        }
        return client.post(
            f"{MEMBERSHIPS_ENDPOINT}/create?data_product_id={str(data_product_id)}",
            json=data,
        )

    @staticmethod
    def approve_default_data_product_dataset_link(client, link_id):
        return client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/approve/{link_id}")

    @staticmethod
    def deny_default_data_product_dataset_link(client, link_id):
        return client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/deny/{link_id}")

    @staticmethod
    def approve_default_data_output_dataset_link(client, link_id):
        return client.post(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/approve/{link_id}")

    @staticmethod
    def deny_default_data_output_dataset_link(client, link_id):
        return client.post(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/deny/{link_id}")

    @staticmethod
    def approve_data_product_membership(client, membership_id):
        return client.post(f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/approve")

    @staticmethod
    def deny_data_product_membership(client, membership_id):
        return client.post(f"{MEMBERSHIPS_ENDPOINT}/{membership_id}/deny")

    @staticmethod
    def delete_default_dataset(client, dataset_id):
        return client.delete(f"{DATASET_ENDPOINT}/{dataset_id}")

    @staticmethod
    def delete_data_product(client, data_product_id):
        return client.delete(f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}")

    @staticmethod
    def delete_data_output(client, data_output_id):
        return client.delete(f"{DATA_OUTPUTS_ENDPOINT}/{data_output_id}")
