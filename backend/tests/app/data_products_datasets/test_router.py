import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from tests.factories import (
    DataProductDatasetAssociationFactory,
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

DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/data_product_dataset_links"
DATA_PRODUCTS_ENDPOINT = "/api/data_products"


class TestDataProductsDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_request_data_product_link(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory()

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_product_link_private_dataset_no_access(self, client):
        data_product = DataProductFactory()
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 403

    def test_request_data_product_link_private_dataset(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        role = RoleFactory(scope=Scope.DATASET)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_product_remove(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
            ],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory()
        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )

        assert response.status_code == 200

        response = self.request_data_product_dataset_unlink(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_request_data_product_link_by_admin(self, client):
        data_product = DataProductFactory()
        ds = DatasetFactory()

        link = self.request_data_product_dataset_link(client, data_product.id, ds.id)
        assert link.status_code == 200

    def test_approve_data_product_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_approve_data_product_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.approve_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_approved_link_no_role(self, client):
        ds = DatasetFactory()
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.approve_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_deny_data_product_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_deny_data_product_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_deny_link_no_role(self, client):
        ds = DatasetFactory()
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )

        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_remove_data_product_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__REVOKE_DATAPRODUCT_ACCESS],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataProductDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_data_product_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataProductDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_request_dataset_link_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_product_dataset_link(
            client, data_product.id, self.invalid_id
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_dataset_with_product_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(scope=Scope.DATASET, permissions=[Action.DATASET__DELETE])
        DatasetRoleAssignmentFactory(
            user_id=str(user.id), role_id=str(role.id), dataset_id=str(ds.id)
        )
        link = DataProductDatasetAssociationFactory(dataset=ds)
        response = client.get(f"/api/data_products/{link.data_product_id}")
        assert response.json()["dataset_links"][0]["dataset_id"] == str(ds.id)
        response = client.delete(f"/api/datasets/{ds.id}")
        assert response.status_code == 200
        response = client.get(f"/api/data_products/{link.data_product_id}")
        assert len(response.json()["dataset_links"]) == 0

    def test_get_pending_actions_no_action(self, client):
        ds = DatasetFactory()
        DataProductDatasetAssociationFactory(dataset=ds)
        response = client.get(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/actions")
        assert response.json() == []

    def test_get_pending_actions(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
            ],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory(access_type=DatasetAccessType.RESTRICTED)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        response = self.request_data_product_dataset_link(
            client, data_product_id=data_product.id, dataset_id=ds.id
        )
        assert response.status_code == 200
        response = client.get(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/actions")
        assert response.json()[0]["data_product_id"] == str(data_product.id)
        assert response.json()[0]["status"] == "pending"

    def test_get_pending_actions_public(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
            ],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory()

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200
        response = client.get(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/actions")
        assert response.json() == []

    def test_history_event_created_on_link_request(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory()

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200
        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 1

    def test_history_event_created_on_remove_link(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__REVOKE_DATAPRODUCT_ACCESS],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataProductDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, link.data_product_id).json()
        assert len(history) == 1

    def test_history_event_created_on_approval(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.approve_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, link.data_product_id).json()
        assert len(history) == 1

    def test_history_event_created_on_denial(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, link.data_product_id).json()
        assert len(history) == 1

    def test_history_event_created_on_unlink_request(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
            ],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory()
        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )

        assert response.status_code == 200

        response = self.request_data_product_dataset_unlink(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 2

    @staticmethod
    def request_data_product_dataset_link(
        client: TestClient, data_product_id, dataset_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def approve_default_data_product_dataset_link(
        client: TestClient, link_id
    ) -> Response:
        return client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/approve/{link_id}")

    @staticmethod
    def deny_default_data_product_dataset_link(client: TestClient, link_id) -> Response:
        return client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/deny/{link_id}")

    @staticmethod
    def remove_data_product_dataset_link(client: TestClient, link_id) -> Response:
        return client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/remove/{link_id}")

    @staticmethod
    def request_data_product_dataset_unlink(
        client: TestClient, data_product_id, dataset_id
    ) -> Response:
        return client.delete(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def get_data_product_history(client, data_product_id):
        return client.get(f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/history")
