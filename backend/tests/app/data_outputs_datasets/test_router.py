import pytest
from tests.factories import (
    DataOutputDatasetAssociationFactory,
    DataOutputFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz import Action
from app.datasets.enums import DatasetAccessType
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Scope

DATA_OUTPUTS_DATASETS_ENDPOINT = "/api/data_output_dataset_links"
DATA_OUTPUTS_ENDPOINT = "/api/data_outputs"


class TestDataOutputsDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_request_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory()

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200

    def test_request_already_exists(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory()

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200
        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 400

    def test_request_data_output_link_private_dataset_no_access(self, client):
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 403

    def test_request_data_output_link_private_dataset(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200

    def test_request_data_output_remove(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)

        assert response.status_code == 200

        response = self.request_data_output_dataset_unlink(
            client, data_output.id, ds.id
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_request_data_output_link_by_admin(self, client):
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)

        ds = DatasetFactory()

        link = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert link.status_code == 200

    def test_approve_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_approve_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_not_owner_cannot_approved_link(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_deny_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_deny_data_output_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_not_owner_cannot_deny_link(self, client):
        ds = DatasetFactory()
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_remove_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__REVOKE_DATA_OUTPUT_LINK],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
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
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        response = self.request_data_output_dataset_link(
            client, data_output.id, self.invalid_id
        )
        assert response.status_code == 403

    def test_delete_dataset_with_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(scope=Scope.DATASET, permissions=[Action.DATASET__DELETE])
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(dataset=ds)
        response = client.get(f"/api/data_outputs/{link.data_output_id}")
        assert response.json()["dataset_links"][0]["dataset_id"] == str(ds.id)
        response = client.delete(f"/api/datasets/{ds.id}")
        assert response.status_code == 200
        response = client.get(f"/api/data_outputs/{link.data_output_id}")
        assert len(response.json()["dataset_links"]) == 0

    def test_get_pending_actions_no_action(self, client):
        ds = DatasetFactory()
        DataOutputDatasetAssociationFactory(dataset=ds)
        response = client.get(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/actions")
        assert response.json() == []

    def test_get_pending_actions(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200
        response = client.get(f"{DATA_OUTPUTS_DATASETS_ENDPOINT}/actions")
        assert response.json()[0]["data_output_id"] == str(data_output.id)
        assert response.json()[0]["status"] == "pending"

    def test_history_event_created_on_request_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory()

        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, data_output.id).json()
        assert len(history) == 1

    def test_history_event_created_on_remove_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__REVOKE_DATA_OUTPUT_LINK],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, link.data_output_id).json()
        assert len(history) == 1

    def test_history_event_created_on_approve_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, link.data_output_id).json()
        assert len(history) == 1

    def test_history_event_created_on_deny_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataOutputDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_default_data_output_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, link.data_output_id).json()
        assert len(history) == 1

    def test_history_event_created_on_unlink_data_output_link(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_output_dataset_link(client, data_output.id, ds.id)

        assert response.status_code == 200

        response = self.request_data_output_dataset_unlink(
            client, data_output.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_output_history(client, data_output.id).json()
        assert len(history) == 2

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

    @staticmethod
    def request_data_output_dataset_unlink(client, data_output_id, dataset_id):
        return client.delete(
            f"{DATA_OUTPUTS_ENDPOINT}/{data_output_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def get_data_output_history(client, data_output_id):
        return client.get(f"{DATA_OUTPUTS_ENDPOINT}/{data_output_id}/history")
