import pytest
from tests.factories import (
    DataOutputDatasetAssociationFactory,
    DataProductMembershipFactory,
    DatasetFactory,
    UserFactory,
)
from tests.factories.data_output import DataOutputFactory

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus

DATA_OUTPUTS_DATASETS_ENDPOINT = "/api/data_output_dataset_links"
DATA_OUTPUTS_ENDPOINT = "/api/data_outputs"


class TestDataOutputsDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_request_data_output_link(self, client):
        membership = DataProductMembershipFactory(user=UserFactory(external_id="sub"))
        data_output = DataOutputFactory(owner=membership.data_product)
        ds = DatasetFactory()

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_request_data_output_link_by_admin(self, client):
        membership = DataProductMembershipFactory()
        data_output = DataOutputFactory(owner=membership.data_product)

        ds = DatasetFactory()

        link = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert link.status_code == 200

    def test_approve_data_output_link(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value
        )
        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_approve_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value
        )

        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_not_owner_cannot_approved_link(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value
        )

        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 403
        assert (
            response.json()["detail"] == "Only dataset owners can execute this action"
        )

    def test_deny_data_output_link(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value
        )
        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_deny_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value
        )

        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_not_owner_cannot_deny_link(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DataOutputDatasetLinkStatus.PENDING_APPROVAL.value
        )

        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 403
        assert (
            response.json()["detail"] == "Only dataset owners can execute this action"
        )

    def test_remove_data_output_link(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        link = DataOutputDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_request_dataset_link_with_invalid_dataset_id(self, client):
        membership = DataProductMembershipFactory(user=UserFactory(external_id="sub"))
        data_output = DataOutputFactory(owner=membership.data_product)
        response = self.request_data_output_dataset_link(
            client, data_output.id, self.invalid_id
        )
        assert response.status_code == 404

    @staticmethod
    def request_data_output_dataset_link(client, data_output_id, dataset_id):
        return client.post(
            f"{DATA_OUTPUTS_ENDPOINT}/{data_output_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def approve_default_data_output_dataset_link(client, link_id):
        return client.post(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/approve/{link_id}")

    @staticmethod
    def deny_default_data_output_dataset_link(client, link_id):
        return client.post(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/deny/{link_id}")

    @staticmethod
    def remove_data_output_dataset_link(client, link_id):
        return client.post(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/remove/{link_id}")
