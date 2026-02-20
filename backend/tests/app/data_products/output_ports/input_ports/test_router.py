from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_ports.enums import OutputPortAccessType
from app.settings import settings
from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

OLD_DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/data_product_dataset_links"
DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/v2/data_products/{}/output_ports/{}/input_ports"
OLD_DATA_PRODUCTS_ENDPOINT = "/api/data_products"
DATA_PRODUCTS_ENDPOINT = "/api/v2/data_products"


class TestDataProductsDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_request_data_product_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
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
        history_response = self.get_data_product_history(client, data_product.id)
        assert history_response.status_code == 200, history_response.text
        assert len(history_response.json()) == 1

    def test_request_data_product_link_deprecated_method(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory()

        response = client.post(
            f"{OLD_DATA_PRODUCTS_ENDPOINT}/{data_product.id}/dataset/{str(ds.id)}",
        )
        assert response.status_code == 200
        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 1

    def test_request_data_product_multiple_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds1 = DatasetFactory()
        ds2 = DatasetFactory()

        response = self.request_data_product_datasets_link(
            client, data_product.id, [ds1.id, ds2.id]
        )
        assert response.status_code == 200
        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 2

    def test_request_already_exists(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
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
        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 400

    def test_request_data_product_link_private_dataset_no_access(self, client):
        data_product = DataProductFactory()
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 403

    def test_request_data_product_link_private_dataset(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory(access_type=OutputPortAccessType.PRIVATE)
        role = RoleFactory(scope=Scope.DATASET)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        response = self.request_data_product_dataset_link(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

    def test_request_data_product_remove_old(self, client):
        assoc = DataProductDatasetAssociationFactory()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=assoc.data_product.id,
        )

        response = self.request_data_product_dataset_unlink_old(
            client, assoc.data_product.id, assoc.dataset.id
        )
        assert response.status_code == 200

    def test_request_data_product_remove(self, client):
        assoc = DataProductDatasetAssociationFactory()
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=assoc.data_product.id,
        )

        response = self.request_data_product_input_port_unlink(
            client,
            assoc.data_product.id,
            assoc.dataset.id,
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_request_data_product_link_by_admin(self, client):
        data_product = DataProductFactory()
        ds = DatasetFactory()

        link = self.request_data_product_dataset_link(client, data_product.id, ds.id)
        assert link.status_code == 200

    def test_approve_data_product_link(self, client):
        link = self.create_link_with_status()
        response = self.approve_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_approve_output_port_as_input_port(self, client):
        link = self.create_link_with_status()
        response = self.approve_output_port_as_input_port(
            client, link.dataset.data_product.id, link.dataset.id, link.data_product.id
        )
        assert response.status_code == 200, response.text

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

    @staticmethod
    def create_link_with_status(status: DecisionStatus = DecisionStatus.PENDING):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
            ],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        return DataProductDatasetAssociationFactory(
            dataset=ds,
            status=status,
        )

    def test_deny_data_product_link(self, client):
        link = self.create_link_with_status()
        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_deny_output_port_as_input_port(self, client):
        link = self.create_link_with_status()
        response = self.deny_output_port_as_input_port(
            client, link.dataset.data_product.id, link.dataset.id, link.data_product.id
        )
        assert response.status_code == 200, response.text

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
        link = self.create_link_with_status()
        response = self.remove_data_product_dataset_link(client, link.id)
        assert response.status_code == 200, response.text

    def test_remove_output_port_as_input_port(self, client):
        link = self.create_link_with_status()
        response = self.remove_output_port_as_input_port(
            client, link.dataset.data_product.id, link.dataset.id, link.data_product.id
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_remove_data_product_link_by_admin(self, client):
        ds = DatasetFactory()
        link = DataProductDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

    def test_request_dataset_link_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        response = self.request_data_product_dataset_link(
            client, data_product.id, self.invalid_id
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_dataset_with_product_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[Action.OUTPUT_PORT__DELETE]
        )
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
        response = client.get(f"{OLD_DATA_PRODUCTS_DATASETS_ENDPOINT}/actions")
        assert response.json() == []

    def test_get_pending_actions(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
            ],
        )
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        ds = DatasetFactory(access_type=OutputPortAccessType.RESTRICTED)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        response = self.request_data_product_dataset_link(
            client, data_product_id=data_product.id, dataset_id=ds.id
        )
        assert response.status_code == 200
        response = client.get(f"{OLD_DATA_PRODUCTS_DATASETS_ENDPOINT}/actions")
        assert response.json()[0]["data_product_id"] == str(data_product.id)
        assert response.json()[0]["status"] == "pending"
        assert response.json()[0]["justification"] == "This is my birth right!"

    def test_get_pending_actions_public(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
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
        response = client.get(f"{OLD_DATA_PRODUCTS_DATASETS_ENDPOINT}/actions")
        assert response.json() == []

    def test_history_event_created_on_remove_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataProductDatasetAssociationFactory(dataset=ds)

        response = self.remove_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, link.data_product_id).json()
        assert len(history) == 1

    def test_history_event_created_on_approval(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
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
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = DatasetFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        link = DataProductDatasetAssociationFactory(
            dataset=ds, status=DecisionStatus.PENDING
        )
        response = self.deny_default_data_product_dataset_link(client, link.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, link.data_product_id).json()
        assert len(history) == 1

    def test_get_input_ports_for_output_port(self, client):
        # Create a dataset (output port) with a data product
        ds = DatasetFactory()

        # Create multiple data products that consume this dataset
        consuming_dp1 = DataProductFactory()
        consuming_dp2 = DataProductFactory()

        # Create associations (links) between consuming data products and the dataset
        DataProductDatasetAssociationFactory(
            dataset=ds, data_product=consuming_dp1, status=DecisionStatus.APPROVED
        )
        DataProductDatasetAssociationFactory(
            dataset=ds, data_product=consuming_dp2, status=DecisionStatus.APPROVED
        )

        # Get the input ports for the output port
        response = client.get(
            DATA_PRODUCTS_DATASETS_ENDPOINT.format(ds.data_product.id, ds.id)
        )

        assert response.status_code == 200
        data = response.json()
        assert "input_ports" in data
        assert len(data["input_ports"]) == 2

        # Verify the consuming data product IDs are in the response
        consuming_dp_ids = {ip["data_product_id"] for ip in data["input_ports"]}
        assert str(consuming_dp1.id) in consuming_dp_ids
        assert str(consuming_dp2.id) in consuming_dp_ids

    def test_history_event_created_on_unlink_request(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
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

        response = self.request_data_product_dataset_unlink_old(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 2

    @staticmethod
    def request_data_product_dataset_link(
        client: TestClient,
        data_product_id: UUID,
        dataset_id: UUID,
        justification: str = "This is my birth right!",
    ) -> Response:
        return TestDataProductsDatasetsRouter.request_data_product_datasets_link(
            client,
            data_product_id,
            [dataset_id],
            justification,
        )

    @staticmethod
    def request_data_product_datasets_link(
        client: TestClient,
        data_product_id: UUID,
        dataset_ids: list[UUID],
        justification: str = "This is my birth right!",
    ) -> Response:
        return client.post(
            f"{OLD_DATA_PRODUCTS_ENDPOINT}/{data_product_id}/link_datasets",
            json={
                "dataset_ids": [str(dataset_id) for dataset_id in dataset_ids],
                "justification": justification,
            },
        )

    @staticmethod
    def approve_default_data_product_dataset_link(
        client: TestClient, link_id
    ) -> Response:
        return client.post(f"{OLD_DATA_PRODUCTS_DATASETS_ENDPOINT}/approve/{link_id}")

    @staticmethod
    def approve_output_port_as_input_port(
        client: TestClient, data_product_id, output_port_id, consuming_data_product_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/approve",
            json={"consuming_data_product_id": f"{consuming_data_product_id}"},
        )

    @staticmethod
    def deny_default_data_product_dataset_link(client: TestClient, link_id) -> Response:
        return client.post(f"{OLD_DATA_PRODUCTS_DATASETS_ENDPOINT}/deny/{link_id}")

    @staticmethod
    def deny_output_port_as_input_port(
        client: TestClient, data_product_id, output_port_id, consuming_data_product_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/deny",
            json={"consuming_data_product_id": f"{consuming_data_product_id}"},
        )

    @staticmethod
    def remove_data_product_dataset_link(client: TestClient, link_id) -> Response:
        return client.post(f"{OLD_DATA_PRODUCTS_DATASETS_ENDPOINT}/remove/{link_id}")

    @staticmethod
    def remove_output_port_as_input_port(
        client: TestClient, data_product_id, output_port_id, consuming_data_product_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/remove",
            json={"consuming_data_product_id": f"{consuming_data_product_id}"},
        )

    @staticmethod
    def request_data_product_dataset_unlink_old(
        client: TestClient, data_product_id, dataset_id
    ) -> Response:
        return client.delete(
            f"{OLD_DATA_PRODUCTS_ENDPOINT}/{data_product_id}/dataset/{dataset_id}"
        )

    @staticmethod
    def request_data_product_input_port_unlink(
        client: TestClient, data_product_id, dataset_id
    ) -> Response:
        return client.delete(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/input_ports/{dataset_id}"
        )

    @staticmethod
    def get_data_product_history(client, data_product_id):
        return client.get(f"{OLD_DATA_PRODUCTS_ENDPOINT}/{data_product_id}/history")
