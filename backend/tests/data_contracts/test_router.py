import pytest
from tests.factories.data_output import DataOutputFactory
from tests.factories.schema import SchemaFactory

ENDPOINT = "/api/data_contracts"


@pytest.fixture
def schema_payload():
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
    @staticmethod
    def create_schema(client, payload):
        return client.post(f"{ENDPOINT}", json=payload)

    @staticmethod
    def get_schemas(client):
        return client.get(f"{ENDPOINT}")

    @staticmethod
    def get_schema_by_id(client, schema_id):
        return client.get(f"{ENDPOINT}/{schema_id}")

    @staticmethod
    def delete_schema(client, schema_id):
        return client.delete(f"{ENDPOINT}/{schema_id}")

    def test_create_schema(self, schema_payload, client):
        created_schema = self.create_schema(client, schema_payload)
        assert created_schema.status_code == 200
        assert "id" in created_schema.json()

    def test_get_schemas(self, client):
        schema = SchemaFactory()
        response = self.get_schemas(client)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(schema.id)

    def test_get_schema_by_id(self, client):
        schema = SchemaFactory()
        response = self.get_schema_by_id(client, schema.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(schema.id)

    def test_remove_schema(self, client):
        schema = SchemaFactory()
        response = self.delete_schema(client, schema.id)
        assert response.status_code == 200
