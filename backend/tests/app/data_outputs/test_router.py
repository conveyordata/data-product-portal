import uuid
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from tests.factories import (
    DataOutputFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    PlatformServiceFactory,
    RoleFactory,
    TagFactory,
    UserFactory,
)

from app.core.authz import Action
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.s3.schema import S3DataOutput
from app.data_outputs.schema_request import DataOutputResultStringRequest
from app.roles.schema import Scope
from app.settings import settings

ENDPOINT = "/api/data_outputs"


@pytest.fixture
def data_output_payload():
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    data_product = DataProductFactory()
    service = PlatformServiceFactory()
    tag = TagFactory()

    return {
        "name": "Data Output Name",
        "description": "Updated Data Output Description",
        "namespace": "namespace-updated",
        "sourceAligned": True,
        "configuration": {
            "bucket": "test",
            "path": "test",
            "configuration_type": "S3DataOutput",
        },
        "owner_id": str(data_product.id),
        "platform_id": str(service.platform.id),
        "service_id": str(service.id),
        "status": "pending",
        "tag_ids": [str(tag.id)],
        "user_id": str(user.id),
    }


@pytest.fixture
def data_output_payload_not_owner():
    data_product = DataProductFactory()
    service = PlatformServiceFactory()
    tag = TagFactory()

    return {
        "name": "Data Output Name",
        "description": "Updated Data Output Description",
        "namespace": "namespace",
        "sourceAligned": True,
        "configuration": {
            "bucket": "test",
            "path": "test",
            "configuration_type": "S3DataOutput",
        },
        "owner_id": str(data_product.id),
        "platform_id": str(service.platform.id),
        "service_id": str(service.id),
        "status": "pending",
        "tag_ids": [str(tag.id)],
    }


class TestDataOutputsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_data_output_source_aligned(
        self, data_output_payload, client: TestClient
    ):
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=data_output_payload["user_id"],
            role_id=role.id,
            data_product_id=data_output_payload["owner_id"],
        )
        created_data_output = self.create_data_output(client, data_output_payload)
        assert created_data_output.status_code == 200
        assert "id" in created_data_output.json()

    def test_create_data_output_product_aligned(
        self, data_output_payload, client: TestClient
    ):
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=data_output_payload["user_id"],
            role_id=role.id,
            data_product_id=data_output_payload["owner_id"],
        )
        payload = deepcopy(data_output_payload)
        payload["sourceAligned"] = False

        created_data_output = self.create_data_output(client, payload)
        assert created_data_output.status_code == 200
        assert "id" in created_data_output.json()

    def test_create_data_output_not_product_owner(
        self, data_output_payload_not_owner, client: TestClient
    ):
        created_data_output = self.create_data_output(
            client, data_output_payload_not_owner
        )
        assert created_data_output.status_code == 403

    def test_get_data_outputs(self, client):
        data_output = DataOutputFactory()
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(data_output.id)

    def test_get_data_output_by_id(self, client: TestClient):
        data_output = DataOutputFactory()

        response = self.get_data_output_by_id(client, data_output.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_output.id)

    def test_get_data_output_by_id_not_found(self, client: TestClient):
        response = self.get_data_output_by_id(client, uuid.uuid4())
        assert response.status_code == 404

    def test_update_data_output(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        tag = TagFactory()
        data_output = DataOutputFactory(owner=data_product)
        update_payload = {
            "name": "update",
            "description": "update",
            "tag_ids": [str(tag.id)],
        }
        response = self.update_data_output(client, update_payload, data_output.id)

        assert response.status_code == 200
        assert response.json()["id"] == str(data_output.id)

    def test_update_data_product_no_member(self, client: TestClient):
        data_output = DataOutputFactory()
        response = self.update_data_output(
            client, {"name": "update", "description": "update"}, data_output.id
        )
        assert response.status_code == 403

    def test_remove_data_output_no_access(self, client: TestClient):
        data_output = DataOutputFactory()
        response = self.delete_data_output(client, data_output.id)
        assert response.status_code == 403

    def test_remove_data_output(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        data_output = DataOutputFactory(owner=data_product)
        response = self.delete_data_output(client, data_output.id)
        assert response.status_code == 200

    def test_update_status_not_owner(self, client: TestClient):
        do = DataOutputFactory()
        response = self.update_data_output_status(client, {"status": "active"}, do.id)
        assert response.status_code == 403

    def test_update_status(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        data_output = DataOutputFactory(owner=data_product)
        response = self.get_data_output_by_id(client, data_output.id)
        assert response.json()["status"] == "active"
        _ = self.update_data_output_status(
            client, {"status": "pending"}, data_output.id
        )
        response = self.get_data_output_by_id(client, data_output.id)
        assert response.json()["status"] == "pending"

    def test_get_graph_data(self, client: TestClient):
        data_output = DataOutputFactory()
        response = client.get(f"{ENDPOINT}/{data_output.id}/graph")
        assert response.json()["edges"] == [
            {
                "animated": True,
                "id": f"{str(data_output.id)}-{str(data_output.owner.id)}",
                "source": str(data_output.owner.id),
                "target": str(data_output.id),
                "sourceHandle": "right_s",
                "targetHandle": "left_t",
            }
        ]
        for node in response.json()["nodes"]:
            if node["type"] == "dataOutputNode":
                assert node == {
                    "data": {
                        "icon_key": "S3DataOutput",
                        "id": str(data_output.id),
                        "link_to_id": str(data_output.owner.id),
                        "name": data_output.name,
                        "domain": None,
                        "domain_id": None,
                        "assignments": None,
                        "description": None,
                    },
                    "id": str(data_output.id),
                    "isMain": True,
                    "type": "dataOutputNode",
                }
            else:
                assert node == {
                    "data": {
                        "icon_key": "default",
                        "id": str(data_output.owner.id),
                        "link_to_id": None,
                        "name": data_output.owner.name,
                        "domain": None,
                        "domain_id": None,
                        "assignments": None,
                        "description": None,
                    },
                    "id": str(data_output.owner.id),
                    "isMain": False,
                    "type": "dataProductNode",
                }

    def test_get_namespace_suggestion_substitution(self, client: TestClient):
        name = "test with spaces"
        response = self.get_namespace_suggestion(client, name)
        body = response.json()

        assert response.status_code == 200
        assert body["namespace"] == "test-with-spaces"

    def test_get_namespace_length_limits(self, client):
        response = self.get_namespace_length_limits(client)
        assert response.status_code == 200
        assert response.json()["max_length"] > 1

    def test_create_data_output_duplicate_namespace(
        self, data_output_payload, client: TestClient
    ):
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_DATA_OUTPUT],
        )
        owner = DataProductFactory()
        DataProductRoleAssignmentFactory(
            user_id=data_output_payload["user_id"],
            role_id=role.id,
            data_product_id=owner.id,
        )
        DataOutputFactory(
            namespace=data_output_payload["namespace"],
            owner=owner,
        )

        create_payload = deepcopy(data_output_payload)
        create_payload["owner_id"] = str(owner.id)

        response = self.create_data_output(client, create_payload)
        assert response.status_code == 400

    def test_create_data_output_invalid_characters_namespace(
        self, data_output_payload, client: TestClient
    ):
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=data_output_payload["user_id"],
            role_id=role.id,
            data_product_id=data_output_payload["owner_id"],
        )
        create_payload = deepcopy(data_output_payload)
        create_payload["namespace"] = "!"

        response = self.create_data_output(client, create_payload)
        assert response.status_code == 400

    def test_create_data_output_invalid_length_namespace(
        self, data_output_payload, client: TestClient
    ):
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=data_output_payload["user_id"],
            role_id=role.id,
            data_product_id=data_output_payload["owner_id"],
        )
        create_payload = deepcopy(data_output_payload)
        create_payload["namespace"] = "a" * 256

        response = self.create_data_output(client, create_payload)
        assert response.status_code == 400

    def test_history_event_created_on_data_output_creation(
        self, data_output_payload, client
    ):
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__CREATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=data_output_payload["user_id"],
            role_id=role.id,
            data_product_id=data_output_payload["owner_id"],
        )
        created_data_output = self.create_data_output(client, data_output_payload)
        assert created_data_output.status_code == 200
        assert "id" in created_data_output.json()

        history = self.get_data_output_history(
            client, created_data_output.json().get("id")
        ).json()
        assert len(history) == 1

    def test_history_event_created_on_data_output_status_update(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        data_output = DataOutputFactory(owner=data_product)
        response = self.update_data_output_status(
            client, {"status": "pending"}, data_output.id
        )
        response = self.get_data_output_by_id(client, data_output.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, data_output.id).json()
        assert len(history) == 1

    def test_history_event_created_on_data_output_update(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        tag = TagFactory()
        data_output = DataOutputFactory(owner=data_product)
        update_payload = {
            "name": "update",
            "description": "update",
            "tag_ids": [str(tag.id)],
        }
        response = self.update_data_output(client, update_payload, data_output.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, data_output.id).json()
        assert len(history) == 1

    def test_history_event_created_on_data_output_deletion(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        data_output = DataOutputFactory(owner=data_product)
        response = self.delete_data_output(client, data_output.id)
        assert response.status_code == 200

        history = self.get_data_output_history(client, data_output.id).json()
        assert len(history) == 1

    def test_retain_deleted_data_output_name_in_history(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_DATA_OUTPUT],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        data_output = DataOutputFactory(owner=data_product)
        data_output_id = data_output.id
        data_output_name = data_output.name

        response = self.delete_data_output(client, data_output.id)
        assert response.status_code == 200

        response = self.get_data_output_history(client, data_output_id)
        assert len(response.json()) == 1
        assert response.json()[0]["deleted_subject_identifier"] == data_output_name

    def test_get_result_string(self, client):
        service = PlatformServiceFactory(
            result_string_template="{bucket}/{suffix}/{path}"
        )
        configuration = S3DataOutput(
            bucket="bucket",
            suffix="suffix",
            path="path",
            configuration_type=DataOutputTypes.S3DataOutput,
        )
        request = DataOutputResultStringRequest(
            platform_id=service.platform.id,
            service_id=service.id,
            configuration=configuration,
        ).model_dump(mode="json")

        response = self.get_data_output_result_string(client, request)
        assert response.status_code == 200
        assert response.json() == "bucket/suffix/path"

    @staticmethod
    def create_data_output(client: TestClient, default_data_output_payload) -> Response:
        return client.post(
            f"/api/data_products/"
            f"{default_data_output_payload.get('owner_id')}/data_output",
            json=default_data_output_payload,
        )

    @staticmethod
    def get_data_output_by_id(client: TestClient, data_output_id) -> Response:
        return client.get(f"{ENDPOINT}/{data_output_id}")

    @staticmethod
    def update_data_output(client: TestClient, payload, data_output_id) -> Response:
        return client.put(f"{ENDPOINT}/{data_output_id}", json=payload)

    @staticmethod
    def delete_data_output(client: TestClient, data_output_id) -> Response:
        return client.delete(f"{ENDPOINT}/{data_output_id}")

    @staticmethod
    def update_data_output_status(
        client: TestClient, status, data_output_id
    ) -> Response:
        return client.put(f"{ENDPOINT}/{data_output_id}/status", json=status)

    @staticmethod
    def get_namespace_suggestion(client: TestClient, name) -> Response:
        return client.get(f"{ENDPOINT}/namespace_suggestion?name={name}")

    @staticmethod
    def get_namespace_length_limits(client: TestClient) -> Response:
        return client.get(f"{ENDPOINT}/namespace_length_limits")

    @staticmethod
    def get_data_output_history(client, data_output_id):
        return client.get(f"{ENDPOINT}/{data_output_id}/history")

    @staticmethod
    def get_data_output_result_string(client, payload):
        return client.post(f"{ENDPOINT}/result_string", json=payload)
