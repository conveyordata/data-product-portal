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

from app.notifications.enums import NotificationTypes
from app.role_assignments.enums import DecisionStatus

NOTIFICATIONS_ENDPOINT = "/api/notifications"
DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/data_product_dataset_links"
DATA_PRODUCTS_ENDPOINT = "/api/data_products"
DATA_OUTPUTS_ENDPOINT = "/api/data_outputs"
MEMBERSHIPS_ENDPOINT = "/api/data_product_memberships"
DATASET_ENDPOINT = "/api/datasets"
DATA_OUTPUTS_DATASETS_ENDPOINT = "/api/data_output_dataset_links"


class TestNotificationsRouter:

    def test_get_approved_notifications_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        data_product_dataset_link = DataProductDatasetAssociationFactory(
            requested_by=owner, status=DecisionStatus.PENDING
        )

        response = self.approve_default_data_product_dataset_link(
            client, data_product_dataset_link.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification_type"] == "DataProductDatasetNotification"
        )
        assert response.json()[0]["data_product_dataset"]["data_product_id"] == str(
            data_product_dataset_link.data_product.id
        )
        assert response.json()[0]["data_product_dataset"]["status"] == "approved"
        assert response.json()[0]["data_product_dataset"]["requested_by"]["id"] == str(
            owner.id
        )

    def test_get_approved_notifications_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        data_output_dataset_link = DataOutputDatasetAssociationFactory(
            requested_by=owner, status=DecisionStatus.PENDING
        )

        response = self.approve_default_data_output_dataset_link(
            client, data_output_dataset_link.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification_type"] == "DataOutputDatasetNotification"
        )
        assert response.json()[0]["data_output_dataset"]["data_output_id"] == str(
            data_output_dataset_link.data_output.id
        )
        assert response.json()[0]["data_output_dataset"]["status"] == "approved"
        assert response.json()[0]["data_output_dataset"]["requested_by"]["id"] == str(
            owner.id
        )

    def test_get_approved_notifications_data_product_membership(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        data_product_membership_link = DataProductMembershipFactory(
            user=owner, status=DecisionStatus.PENDING
        )

        response = self.approve_data_product_membership(
            client, data_product_membership_link.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification_type"]
            == "DataProductMembershipNotification"
        )
        assert response.json()[0]["data_product_membership"]["data_product_id"] == str(
            data_product_membership_link.data_product.id
        )
        assert response.json()[0]["data_product_membership"]["status"] == "approved"
        assert response.json()[0]["data_product_membership"]["user"]["id"] == str(
            owner.id
        )

    def test_get_denied_notifications_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        data_product_dataset_link = DataProductDatasetAssociationFactory(
            requested_by=owner, status=DecisionStatus.PENDING
        )

        response = self.deny_default_data_product_dataset_link(
            client, data_product_dataset_link.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification_type"] == "DataProductDatasetNotification"
        )
        assert response.json()[0]["data_product_dataset"]["data_product_id"] == str(
            data_product_dataset_link.data_product.id
        )
        assert response.json()[0]["data_product_dataset"]["status"] == "denied"
        assert response.json()[0]["data_product_dataset"]["requested_by"]["id"] == str(
            owner.id
        )

    def test_get_denied_notifications_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        data_output_dataset_link = DataOutputDatasetAssociationFactory(
            requested_by=owner, status=DecisionStatus.PENDING
        )

        response = self.deny_default_data_output_dataset_link(
            client, data_output_dataset_link.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification_type"] == "DataOutputDatasetNotification"
        )
        assert response.json()[0]["data_output_dataset"]["data_output_id"] == str(
            data_output_dataset_link.data_output.id
        )
        assert response.json()[0]["data_output_dataset"]["status"] == "denied"
        assert response.json()[0]["data_output_dataset"]["requested_by"]["id"] == str(
            owner.id
        )

    def test_get_denied_notifications_data_product_membership(self, client):
        owner = UserFactory(external_id="sub", is_admin=True)
        data_product_membership_link = DataProductMembershipFactory(
            user=owner, status=DecisionStatus.PENDING
        )

        response = self.deny_data_product_membership(
            client, data_product_membership_link.id
        )
        assert response.status_code == 200

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert (
            response.json()[0]["notification_type"]
            == "DataProductMembershipNotification"
        )
        assert response.json()[0]["data_product_membership"]["data_product_id"] == str(
            data_product_membership_link.data_product.id
        )
        assert response.json()[0]["data_product_membership"]["status"] == "denied"
        assert response.json()[0]["data_product_membership"]["user"]["id"] == str(
            owner.id
        )

    def test_delete_parent_dataset_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[owner])
        link = DataProductDatasetAssociationFactory(
            dataset=ds,
            status=DecisionStatus.APPROVED,
        )
        DataProductDatasetNotificationFactory(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            data_product_dataset=link,
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["data_product_dataset"]["id"] == str(link.id)
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_dataset_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[owner])
        link = DataOutputDatasetAssociationFactory(
            dataset=ds,
            status=DecisionStatus.APPROVED,
        )
        DataOutputDatasetNotificationFactory(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            data_output_dataset=link,
            user=owner,
        )

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["data_output_dataset"]["id"] == str(link.id)
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_product_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataProductDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
            data_product=(DataProductMembershipFactory(user=owner).data_product),
        )
        DataProductDatasetNotificationFactory(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            data_product_dataset=link,
            user=owner,
        )

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["data_product_dataset"]["id"] == str(link.id)
        response = self.delete_data_product(client, link.data_product.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_product_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataOutputDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
            data_output=DataOutputFactory(
                owner=(DataProductMembershipFactory(user=owner).data_product)
            ),
        )
        DataOutputDatasetNotificationFactory(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            data_output_dataset=link,
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["data_output_dataset"]["id"] == str(link.id)
        response = self.delete_data_product(client, link.data_output.owner.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_product_data_product_membership(self, client):
        owner = UserFactory(external_id="sub")
        membership = DataProductMembershipFactory(
            status=DecisionStatus.APPROVED,
            data_product=(DataProductMembershipFactory(user=owner).data_product),
        )
        DataProductMembershipNotificationFactory(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            data_product_membership=membership,
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["data_product_membership"]["id"] == str(membership.id)
        response = self.delete_data_product(client, membership.data_product.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_parent_data_output_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataOutputDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
            data_output=DataOutputFactory(
                owner=(DataProductMembershipFactory(user=owner).data_product)
            ),
        )
        DataOutputDatasetNotificationFactory(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            data_output_dataset=link,
            user=owner,
        )

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json()[0]["data_output_dataset"]["id"] == str(link.id)
        response = self.delete_data_output(client, link.data_output.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_own_notification_data_product_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataProductDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
        )
        notification = DataProductDatasetNotificationFactory(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            data_product_dataset=link,
            user=owner,
        )

        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert len(response.json()) == 1
        response = self.delete_notification(client, notification.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_other_user_notification_data_product_dataset(self, client):
        other = UserFactory()
        link = DataProductDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
        )
        notification = DataProductDatasetNotificationFactory(
            notification_type=NotificationTypes.DataProductDatasetNotification,
            data_product_dataset=link,
            user=other,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert len(response.json()) == 0
        response = self.delete_notification(client, notification.id)
        assert response.status_code == 403

    def test_delete_own_notification_data_output_dataset(self, client):
        owner = UserFactory(external_id="sub")
        link = DataOutputDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
        )
        notification = DataOutputDatasetNotificationFactory(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            data_output_dataset=link,
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert len(response.json()) == 1
        response = self.delete_notification(client, notification.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_other_user_notification_data_output_dataset(self, client):
        other = UserFactory()
        link = DataOutputDatasetAssociationFactory(
            status=DecisionStatus.APPROVED,
        )
        notification = DataOutputDatasetNotificationFactory(
            notification_type=NotificationTypes.DataOutputDatasetNotification,
            data_output_dataset=link,
            user=other,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert len(response.json()) == 0
        response = self.delete_notification(client, notification.id)
        assert response.status_code == 403

    def test_delete_own_notification_data_product_membership(self, client):
        owner = UserFactory(external_id="sub")
        link = DataProductMembershipFactory(
            status=DecisionStatus.APPROVED,
        )
        notification = DataProductMembershipNotificationFactory(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            data_product_membership=link,
            user=owner,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert len(response.json()) == 1
        response = self.delete_notification(client, notification.id)
        assert response.status_code == 200
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert response.json() == []

    def test_delete_other_user_notification_data_product_membership(self, client):
        other = UserFactory()
        link = DataProductMembershipFactory(
            status=DecisionStatus.APPROVED,
        )
        notification = DataProductMembershipNotificationFactory(
            notification_type=NotificationTypes.DataProductMembershipNotification,
            data_product_membership=link,
            user=other,
        )
        response = client.get(f"{NOTIFICATIONS_ENDPOINT}")
        assert len(response.json()) == 0
        response = self.delete_notification(client, notification.id)
        assert response.status_code == 403

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

    @staticmethod
    def delete_notification(client, notification_id):
        return client.delete(f"{NOTIFICATIONS_ENDPOINT}/{notification_id}")
