import pytest
from tests.factories.data_contract import DataContractFactory
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.platform_service import PlatformServiceFactory
from tests.factories.user import UserFactory

ENDPOINT = "/api/data_outputs"


@pytest.fixture
def data_output_payload():
    data_product = DataProductMembershipFactory(
        user=UserFactory(external_id="sub")
    ).data_product
    service = PlatformServiceFactory()

    return {
        "name": "Data Output Name",
        "description": "Updated Data Output Description",
        "external_id": "Updated Data Output External ID",
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
    }


@pytest.fixture
def data_output_payload_not_owner():
    data_product = DataProductFactory()
    service = PlatformServiceFactory()

    return {
        "name": "Data Output Name",
        "description": "Updated Data Output Description",
        "external_id": "Updated Data Output External ID",
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
    }


class TestDataOutputsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_dataoutput(self, data_output_payload, client):
        created_dataoutput = self.create_data_output(client, data_output_payload)
        assert created_dataoutput.status_code == 200
        assert "id" in created_dataoutput.json()

    def test_create_dataoutput_not_product_owner(
        self, data_output_payload_not_owner, client
    ):
        created_dataoutput = self.create_data_output(
            client, data_output_payload_not_owner
        )
        assert created_dataoutput.status_code == 403

    def test_get_data_outputs(self, client):
        data_output = DataOutputFactory()
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(data_output.id)

    def test_get_data_ouptut_by_id(self, client):
        data_output = DataOutputFactory()

        response = self.get_data_output_by_id(client, data_output.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_output.id)

    def test_update_data_product(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        data_output = DataOutputFactory(owner=data_product)
        update_payload = {"name": "update", "description": "update"}
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

    def test_get_data_contracts(self, client):
        data_output = DataOutputFactory()
        data_contract = DataContractFactory(data_output_id=data_output.id)
        response = self.get_data_contracts(client, data_output.id)
        assert response.status_code == 200
        assert response.json()[0]["id"] == str(data_contract.id)

    @staticmethod
    def create_data_output(client, default_data_output_payload):
        return client.post(ENDPOINT, json=default_data_output_payload)

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
    def get_data_contracts(client, data_output_id):
        return client.get(f"{ENDPOINT}/{data_output_id}/data_contracts")
