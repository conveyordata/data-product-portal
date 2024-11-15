import pytest
from tests.factories.data_contract import DataContractFactory
from tests.factories.data_output import DataOutputFactory

ENDPOINT = "/api/data_contracts"


@pytest.fixture
def data_contract_payload():
    data_output = DataOutputFactory()

    return {
        "data_output_id": str(data_output.id),
        "table": "Some table",
        "description": "Some description",
        "checks": "Some checks",
        "columns": [
            {
                "name": "Some column",
                "description": "Some column description",
                "data_type": "Some data type",
                "checks": "Some column checks",
            }
        ],
        "service_level_objectives": [
            {"type": "Some type", "value": "Some value", "severity": "Some severity"}
        ],
    }


class TestDataContractsRouter:
    def test_create_data_contract(self, data_contract_payload, client):
        created_data_contract = self.create_data_contract(client, data_contract_payload)
        assert created_data_contract.status_code == 200
        assert "id" in created_data_contract.json()

    def test_get_data_contracts(self, client):
        data_contract = DataContractFactory()
        response = self.get_data_contracts(client)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(data_contract.id)

    def test_get_data_contract_by_id(self, client):
        data_contract = DataContractFactory()
        response = self.get_data_contract_by_id(client, data_contract.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_contract.id)

    def test_delete_data_contract(self, client):
        data_contract = DataContractFactory()
        response = self.delete_data_contract(client, data_contract.id)
        assert response.status_code == 200

    @staticmethod
    def create_data_contract(client, payload):
        return client.post(f"{ENDPOINT}", json=payload)

    @staticmethod
    def get_data_contracts(client):
        return client.get(f"{ENDPOINT}")

    @staticmethod
    def get_data_contract_by_id(client, data_contract_id):
        return client.get(f"{ENDPOINT}/{data_contract_id}")

    @staticmethod
    def delete_data_contract(client, data_contract_id):
        return client.delete(f"{ENDPOINT}/{data_contract_id}")
