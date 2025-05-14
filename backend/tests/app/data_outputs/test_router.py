from copy import deepcopy

import pytest
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.platform_service import PlatformServiceFactory
from tests.factories.tags import TagFactory
from tests.factories.user import UserFactory

ENDPOINT = "/api/data_outputs"


@pytest.fixture
def data_output_payload():
    data_product = DataProductMembershipFactory(
        user=UserFactory(external_id="sub")
    ).data_product
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

    def test_create_data_output_source_aligned(self, data_output_payload, client):
        created_data_output = self.create_data_output(client, data_output_payload)
        assert created_data_output.status_code == 200
        assert "id" in created_data_output.json()

    def test_create_data_output_product_aligned(self, data_output_payload, client):
        payload = deepcopy(data_output_payload)
        payload["sourceAligned"] = False

        created_data_output = self.create_data_output(client, payload)
        assert created_data_output.status_code == 200
        assert "id" in created_data_output.json()

    def test_create_data_output_not_product_owner(
        self, data_output_payload_not_owner, client
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

    def test_get_data_output_by_id(self, client):
        data_output = DataOutputFactory()

        response = self.get_data_output_by_id(client, data_output.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_output.id)

    def test_update_data_product(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
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

    def test_update_data_product_no_member(self, client):
        data_output = DataOutputFactory()
        response = self.update_data_output(
            client, {"name": "update", "description": "update"}, data_output.id
        )
        assert response.status_code == 403

    def test_remove_data_output_no_member(self, client):
        data_output = DataOutputFactory()
        response = self.delete_data_output(client, data_output.id)
        assert response.status_code == 403

    def test_remove_data_output(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        data_output = DataOutputFactory(owner=data_product)
        response = self.delete_data_output(client, data_output.id)
        assert response.status_code == 200

    def test_update_status_not_owner(self, client):
        do = DataOutputFactory()
        response = self.update_data_output_status(client, {"status": "active"}, do.id)
        assert response.status_code == 403

    def test_update_status(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        data_output = DataOutputFactory(owner=data_product)
        response = self.get_data_output_by_id(client, data_output.id)
        assert response.json()["status"] == "active"
        _ = self.update_data_output_status(
            client, {"status": "pending"}, data_output.id
        )
        response = self.get_data_output_by_id(client, data_output.id)
        assert response.json()["status"] == "pending"

    def test_get_graph_data(self, client):
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
                    },
                    "id": str(data_output.owner.id),
                    "isMain": False,
                    "type": "dataProductNode",
                }

    def test_get_namespace_suggestion_subsitution(self, client):
        name = "test with spaces"
        response = self.get_namespace_suggestion(client, name)
        body = response.json()

        assert response.status_code == 200
        assert body["namespace"] == "test-with-spaces"

    def test_get_namespace_length_limits(self, client):
        response = self.get_namespace_length_limits(client)
        assert response.status_code == 200
        assert response.json()["max_length"] > 1

    def test_create_data_output_duplicate_namespace(self, data_output_payload, client):
        owner = DataProductFactory()
        DataOutputFactory(
            namespace=data_output_payload["namespace"],
            owner=owner,
        )

        create_payload = deepcopy(data_output_payload)
        create_payload["owner_id"] = str(owner.id)

        response = self.create_data_output(client, create_payload)
        assert response.status_code == 400

    def test_create_data_output_invalid_characters_namespace(
        self, data_output_payload, client
    ):
        create_payload = deepcopy(data_output_payload)
        create_payload["namespace"] = "!"

        response = self.create_data_output(client, create_payload)
        assert response.status_code == 400

    def test_create_data_output_invalid_length_namespace(
        self, data_output_payload, client
    ):
        create_payload = deepcopy(data_output_payload)
        create_payload["namespace"] = "a" * 256

        response = self.create_data_output(client, create_payload)
        assert response.status_code == 400

    @staticmethod
    def create_data_output(client, default_data_output_payload):
        return client.post(
            f"/api/data_products/"
            f"{default_data_output_payload.get('owner_id')}/data_output",
            json=default_data_output_payload,
        )

    @staticmethod
    def get_data_output_by_id(client, data_output_id):
        return client.get(f"{ENDPOINT}/{data_output_id}")

    @staticmethod
    def update_data_output(client, payload, data_output_id):
        return client.put(f"{ENDPOINT}/{data_output_id}", json=payload)

    @staticmethod
    def delete_data_output(client, data_output_id):
        return client.delete(f"{ENDPOINT}/{data_output_id}")

    @staticmethod
    def update_data_output_status(client, status, data_output_id):
        return client.put(f"{ENDPOINT}/{data_output_id}/status", json=status)

    @staticmethod
    def get_namespace_suggestion(client, name):
        return client.get(f"{ENDPOINT}/namespace_suggestion?name={name}")

    @staticmethod
    def get_namespace_length_limits(client):
        return client.get(f"{ENDPOINT}/namespace_length_limits")
