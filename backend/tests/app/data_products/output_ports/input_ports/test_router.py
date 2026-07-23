from datetime import date, timedelta
from typing import Optional
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_ports.enums import OutputPortAccessType
from app.settings import settings
from tests.factories import (
    AccessDurationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    ExplorationFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/v2/data_products/{}/output_ports/{}/input_ports"
DATA_PRODUCTS_ENDPOINT = "/api/v2/data_products"


class TestInputPortsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_request_input_ports_for_data_product(self, client):
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
        ds = OutputPortFactory()

        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )
        assert response.status_code == 200
        history_response = self.get_data_product_history(client, data_product.id)
        assert history_response.status_code == 200, history_response.text
        assert len(history_response.json()) == 1

    def test_request_input_ports_for_data_product_deprecated(self, client):
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
        ds = OutputPortFactory()

        response = self.request_input_ports_for_data_product_deprecated(
            client, data_product.id, [ds.id]
        )
        assert response.status_code == 200
        history_response = self.get_data_product_history(client, data_product.id)
        assert history_response.status_code == 200, history_response.text
        assert len(history_response.json()) == 1

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
        ds1 = OutputPortFactory()
        ds2 = OutputPortFactory()

        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds1.id, ds2.id]
        )
        assert response.status_code == 200, response.text
        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history["events"]) == 2

    def test_request_input_ports_for_data_product_already_exists(self, client):
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
        ds = OutputPortFactory()

        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )
        assert response.status_code == 200
        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )
        assert response.status_code == 400

    def test_renew_input_port_for_data_product(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        ds = OutputPortFactory(
            access_type=OutputPortAccessType.RESTRICTED,
            data_product_access_duration_type=AccessDurationType.TIME_BOUND,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
        )
        assoc = InputPortFactory(
            output_port=ds,
            status=DecisionStatus.APPROVED,
            request__access_duration_type=AccessDurationType.TIME_BOUND,
            request__valid_until=date.today() + timedelta(days=10),
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = self.renew_input_port_for_data_product(
            client, assoc.consuming_abstract_data_product.id, ds.id
        )
        assert response.status_code == 200, response.text

    def test_renew_input_port_for_data_product__no_existing_link(self, client):
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
        ds = OutputPortFactory()

        response = self.renew_input_port_for_data_product(
            client, data_product.id, ds.id
        )
        assert response.status_code == 404

    def test_renew_input_port_for_data_product__pending_request(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS],
        )
        assoc = InputPortFactory(status=DecisionStatus.PENDING)
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = self.renew_input_port_for_data_product(
            client,
            assoc.consuming_abstract_data_product.id,
            assoc.output_port.id,
        )
        assert response.status_code == 400

    def test_request_input_ports_for_data_product_private_dataset_no_access(
        self, client
    ):
        data_product = DataProductFactory()
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)

        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )
        assert response.status_code == 403

    def test_request_input_ports_for_data_product_private_dataset(self, client):
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
        ds = OutputPortFactory(access_type=OutputPortAccessType.PRIVATE)
        role = RoleFactory(scope=Scope.DATASET)
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )
        assert response.status_code == 200

    def test_request_data_product_remove_old(self, client):
        assoc = InputPortFactory()
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
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = self.revoke_input_port_for_data_product(
            client, assoc.consuming_abstract_data_product.id, assoc.output_port.id
        )
        assert response.status_code == 200

    def test_request_data_product_remove(self, client):
        assoc = InputPortFactory()
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
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = self.revoke_input_port_for_data_product(
            client,
            assoc.consuming_abstract_data_product.id,
            assoc.output_port.id,
        )
        assert response.status_code == 200

    def test_cancel_input_port_for_data_product(self, client):
        assoc = InputPortFactory(status=DecisionStatus.PENDING)
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
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{assoc.consuming_abstract_data_product.id}"
            f"/input_ports/{assoc.output_port.id}/cancel"
        )
        assert response.status_code == 200

    def test_cancel_input_port_for_data_product_blocked_when_approved(self, client):
        assoc = InputPortFactory(status=DecisionStatus.APPROVED)
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
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{assoc.consuming_abstract_data_product.id}"
            f"/input_ports/{assoc.output_port.id}/cancel"
        )
        assert response.status_code == 400

    def test_remove_input_port_for_data_product_hard_deletes_regardless_of_status(
        self, client
    ):
        assoc = InputPortFactory(status=DecisionStatus.APPROVED)
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
            data_product_id=assoc.consuming_abstract_data_product.id,
        )

        response = client.delete(
            f"{DATA_PRODUCTS_ENDPOINT}/{assoc.consuming_abstract_data_product.id}"
            f"/input_ports/{assoc.output_port.id}"
        )
        assert response.status_code == 200

        get_response = client.get(
            f"{DATA_PRODUCTS_ENDPOINT}/{assoc.consuming_abstract_data_product.id}/input_ports"
        )
        assert get_response.json()["input_ports"] == []

    @pytest.mark.usefixtures("admin")
    def test_request_data_product_link_by_admin(self, client):
        data_product = DataProductFactory()
        ds = OutputPortFactory()

        link = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )
        assert link.status_code == 200

    def test_approve_output_port_as_input_port(self, client):
        link = self.create_link_with_status()
        response = self.approve_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200, response.text

    def test_approve_output_port_as_input_port_reasoning(self, client):
        link = self.create_link_with_status()
        response = self.approve_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
            decisionNote="I think this is a great use case!",
        )
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_approve_data_product_link_by_admin(self, client):
        ds = OutputPortFactory()
        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)

        response = self.approve_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200

    def test_approved_link_no_role(self, client):
        ds = OutputPortFactory()
        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)

        response = self.approve_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    @staticmethod
    def create_link_with_status(status: DecisionStatus = DecisionStatus.PENDING):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        return InputPortFactory(
            output_port=ds,
            status=status,
        )

    def test_deny_output_port_as_input_port(self, client):
        link = self.create_link_with_status()
        response = self.deny_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200, response.text

    def test_deny_output_port_as_input_port_blocked_when_approved(self, client):
        link = self.create_link_with_status(DecisionStatus.APPROVED)
        response = self.deny_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 400, response.text

    def test_deny_output_port_as_input_port_reasoning_required(self, client):
        link = self.create_link_with_status()
        response = client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(link.output_port.data_product.id, link.output_port.id)}/deny",
            json={
                "consuming_data_product_id": f"{link.consuming_abstract_data_product.id}"
            },
        )
        assert response.status_code == 422, response.text

    @pytest.mark.usefixtures("admin")
    def test_deny_data_product_link_by_admin(self, client):
        ds = OutputPortFactory()
        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)

        response = self.deny_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200

    def test_deny_link_no_role(self, client):
        ds = OutputPortFactory()
        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)

        response = self.deny_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    def test_revoke_output_port_as_input_port(self, client):
        link = self.create_link_with_status(DecisionStatus.APPROVED)
        response = self.revoke_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200, response.text

    def test_revoke_output_port_as_input_port_blocked_when_no_active_grant(
        self, client
    ):
        link = self.create_link_with_status(DecisionStatus.PENDING)
        response = self.revoke_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 400, response.text

    def test_remove_output_port_as_input_port_hard_deletes_regardless_of_status(
        self, client
    ):
        link = self.create_link_with_status(DecisionStatus.APPROVED)
        consuming_data_product_id = link.consuming_abstract_data_product.id
        response = self.remove_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            consuming_data_product_id,
        )
        assert response.status_code == 200, response.text

        history = self.get_data_product_history(
            client, consuming_data_product_id
        ).json()
        assert len(history) == 1

    def test_revoke_link_no_role(self, client):
        ds = OutputPortFactory()
        link = InputPortFactory(output_port=ds, status=DecisionStatus.APPROVED)

        response = self.revoke_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"]
            == "You don't have permission to perform this action"
        )

    @pytest.mark.usefixtures("admin")
    def test_revoke_data_product_link_by_admin(self, client):
        ds = OutputPortFactory()
        link = InputPortFactory(output_port=ds, status=DecisionStatus.APPROVED)

        response = self.revoke_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
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
        response = self.request_input_ports_for_data_product(
            client, data_product.id, [self.invalid_id]
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_dataset_with_product_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[Action.OUTPUT_PORT__DELETE]
        )
        DatasetRoleAssignmentFactory(
            user_id=str(user.id), role_id=str(role.id), output_port_id=str(ds.id)
        )
        link = InputPortFactory(output_port=ds)
        response = client.get(
            f"/api/v2/data_products/{link.consuming_abstract_data_product.id}/input_ports"
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["input_ports"]) == 1
        response = client.delete(
            f"/api/v2/data_products/{ds.data_product.id}/output_ports/{ds.id}"
        )
        assert response.status_code == 200
        response = client.get(
            f"/api/v2/data_products/{link.consuming_abstract_data_product.id}/input_ports"
        )
        assert len(response.json()["input_ports"]) == 0

    def test_history_event_created_on_revoke_link(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        link = InputPortFactory(output_port=ds)

        response = self.revoke_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200

        history = self.get_data_product_history(
            client, link.consuming_abstract_data_product.id
        ).json()
        assert len(history) == 1

    def test_history_event_created_on_approval(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)
        response = self.approve_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200

        history = self.get_data_product_history(
            client, link.consuming_abstract_data_product.id
        ).json()
        assert len(history["events"]) == 1

    def test_history_event_created_on_denial(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)
        response = self.deny_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            link.consuming_abstract_data_product.id,
        )
        assert response.status_code == 200

        history = self.get_data_product_history(
            client, link.consuming_abstract_data_product.id
        ).json()
        assert len(history["events"]) == 1

    def test_approve_output_port_as_input_port_for_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        exploration = ExplorationFactory()
        link = InputPortFactory(
            output_port=ds,
            consuming_abstract_data_product=exploration,
            status=DecisionStatus.PENDING,
        )
        response = self.approve_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            exploration.id,
        )
        assert response.status_code == 200, response.text

    def test_deny_output_port_as_input_port_for_exploration(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory()
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        exploration = ExplorationFactory()
        link = InputPortFactory(
            output_port=ds,
            consuming_abstract_data_product=exploration,
            status=DecisionStatus.PENDING,
        )
        response = self.deny_output_port_as_input_port(
            client,
            link.output_port.data_product.id,
            link.output_port.id,
            exploration.id,
        )
        assert response.status_code == 200, response.text

    def test_get_input_ports_for_output_port(self, client):
        # Create a dataset (output port) with a data product
        ds = OutputPortFactory()

        # Create multiple data products that consume this dataset
        consuming_dp1 = DataProductFactory()
        consuming_dp2 = DataProductFactory()

        # Create associations (links) between consuming data products and the dataset
        InputPortFactory(
            output_port=ds,
            consuming_abstract_data_product=consuming_dp1,
            status=DecisionStatus.APPROVED,
        )
        InputPortFactory(
            output_port=ds,
            consuming_abstract_data_product=consuming_dp2,
            status=DecisionStatus.APPROVED,
        )

        # Get the input ports for the output port
        response = client.get(
            DATA_PRODUCTS_DATASETS_ENDPOINT.format(ds.data_product.id, ds.id)
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert "input_ports" in data
        assert len(data["input_ports"]) == 2

        # Verify the consuming data product IDs are in the response
        consuming_dp_ids = {
            ip["consuming_abstract_data_product_id"] for ip in data["input_ports"]
        }
        assert str(consuming_dp1.id) in consuming_dp_ids
        assert str(consuming_dp2.id) in consuming_dp_ids

    def test_history_event_created_on_revoke_request(self, client):
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
        ds = OutputPortFactory()
        response = self.request_input_ports_for_data_product(
            client, data_product.id, [ds.id]
        )

        assert response.status_code == 200

        response = self.revoke_input_port_for_data_product(
            client, data_product.id, ds.id
        )
        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history["events"]) == 2

    @staticmethod
    def request_input_ports_for_data_product(
        client: TestClient,
        data_product_id: UUID,
        output_port_ids: list[UUID],
        justification: str = "This is my birth right!",
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/input_ports",
            json={
                "output_ports": [
                    str(output_port_id) for output_port_id in output_port_ids
                ],
                "justification": justification,
            },
        )

    @staticmethod
    def renew_input_port_for_data_product(
        client: TestClient,
        data_product_id: UUID,
        output_port_id: UUID,
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/input_ports/{output_port_id}/renew"
        )

    @staticmethod
    def request_input_ports_for_data_product_deprecated(
        client: TestClient,
        data_product_id: UUID,
        output_port_ids: list[UUID],
        justification: str = "This is my birth right!",
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/link_input_ports",
            json={
                "input_ports": [
                    str(output_port_id) for output_port_id in output_port_ids
                ],
                "justification": justification,
            },
        )

    @staticmethod
    def approve_output_port_as_input_port(
        client: TestClient,
        data_product_id,
        output_port_id,
        consuming_data_product_id,
        decisionNote: Optional[str] = None,
    ) -> Response:
        body = {"consuming_data_product_id": f"{consuming_data_product_id}"}
        if decisionNote:
            body["decision_note"] = decisionNote
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/approve",
            json=body,
        )

    @staticmethod
    def deny_output_port_as_input_port(
        client: TestClient,
        data_product_id,
        output_port_id,
        consuming_data_product_id,
        decisionNote: str = "Denied?!",
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/deny",
            json={
                "consuming_data_product_id": f"{consuming_data_product_id}",
                "decision_note": decisionNote,
            },
        )

    @staticmethod
    def revoke_output_port_as_input_port(
        client: TestClient, data_product_id, output_port_id, consuming_data_product_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/revoke",
            json={"consuming_data_product_id": f"{consuming_data_product_id}"},
        )

    @staticmethod
    def remove_output_port_as_input_port(
        client: TestClient, data_product_id, output_port_id, consuming_data_product_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/remove",
            json={"consuming_data_product_id": f"{consuming_data_product_id}"},
        )

    @staticmethod
    def revoke_input_port_for_data_product(
        client: TestClient, data_product_id, output_port_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/input_ports/{output_port_id}/revoke"
        )

    @staticmethod
    def get_data_product_history(client, data_product_id):
        return client.get(f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/history")


class TestInputPortConsumptionTracking:
    """Tests that PostHog consumption events are fired correctly.

    Consumption (Input Port Approved) is a key success metric for the portal
    — it measures how actively data products are being used by other teams.
    """

    def test_posthog_capture_called_on_unrestricted_link(self, client):
        """Auto-approved (unrestricted) links must fire a posthog event immediately."""
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
        ds = OutputPortFactory(access_type=OutputPortAccessType.UNRESTRICTED)

        mock_posthog = MagicMock()
        with patch(
            "app.abstract_data_product.service.get_posthog_client",
            return_value=mock_posthog,
        ):
            response = self.request_input_ports_for_data_product(
                client, data_product.id, [ds.id]
            )

        assert response.status_code == 200
        mock_posthog.capture.assert_called_once()
        call_kwargs = mock_posthog.capture.call_args.kwargs
        assert call_kwargs["event"] == "Input Port Approved"
        assert call_kwargs["properties"]["output_port_id"] == str(ds.id)
        assert call_kwargs["properties"]["consuming_data_product_id"] == str(
            data_product.id
        )

    def test_posthog_capture_not_called_on_restricted_link_request(self, client):
        """Restricted links are PENDING — posthog must NOT fire until approved."""
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
        ds = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)

        mock_posthog = MagicMock()
        with patch(
            "app.abstract_data_product.service.get_posthog_client",
            return_value=mock_posthog,
        ):
            response = self.request_input_ports_for_data_product(
                client, data_product.id, [ds.id]
            )

        assert response.status_code == 200
        mock_posthog.capture.assert_not_called()

    def test_posthog_capture_called_on_manual_approval(self, client):
        """Manual approval of a pending link must fire a posthog event."""
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        ds = OutputPortFactory(access_type=OutputPortAccessType.RESTRICTED)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )
        link = InputPortFactory(output_port=ds, status=DecisionStatus.PENDING)

        mock_posthog = MagicMock()
        with patch(
            "app.data_products.output_ports.input_ports.service.get_posthog_client",
            return_value=mock_posthog,
        ):
            response = self.approve_output_port_as_input_port(
                client,
                link.output_port.data_product.id,
                link.output_port.id,
                link.consuming_abstract_data_product.id,
            )

        assert response.status_code == 200, response.text
        mock_posthog.capture.assert_called_once()
        call_kwargs = mock_posthog.capture.call_args.kwargs
        assert call_kwargs["event"] == "Input Port Approved"
        assert call_kwargs["properties"]["output_port_id"] == str(ds.id)
        assert call_kwargs["properties"]["consuming_data_product_id"] == str(
            link.consuming_abstract_data_product.id
        )

    def test_posthog_not_called_when_disabled(self, client):
        """When posthog is disabled (None), no AttributeError and no capture."""
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
        ds = OutputPortFactory(access_type=OutputPortAccessType.UNRESTRICTED)

        with patch(
            "app.abstract_data_product.service.get_posthog_client",
            return_value=None,
        ):
            response = self.request_input_ports_for_data_product(
                client, data_product.id, [ds.id]
            )

        assert response.status_code == 200

    @staticmethod
    def request_input_ports_for_data_product(
        client: TestClient,
        data_product_id: UUID,
        output_port_ids: list[UUID],
        justification: str = "Tracking test justification",
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/input_ports",
            json={
                "output_ports": [str(oid) for oid in output_port_ids],
                "justification": justification,
            },
        )

    @staticmethod
    def approve_output_port_as_input_port(
        client: TestClient, data_product_id, output_port_id, consuming_data_product_id
    ) -> Response:
        return client.post(
            f"{DATA_PRODUCTS_DATASETS_ENDPOINT.format(data_product_id, output_port_id)}/approve",
            json={"consuming_data_product_id": f"{consuming_data_product_id}"},
        )
