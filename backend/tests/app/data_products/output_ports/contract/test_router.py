from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"

CONTRACT_PAYLOAD = {
    "apiVersion": "v3.1.0",
    "kind": "DataContract",
    "id": "clinical-trial-dashboard-contract",
    "schema": [
        {
            "name": "trial_master",
            "logicalType": "object",
            "physicalType": "table",
            "physicalName": "clinical-trial-dashboard.trial_master",
            "description": "Main table of clinical trial performance metrics",
            "properties": [
                {
                    "name": "trial_id",
                    "businessName": "Trial Identifier",
                    "logicalType": "string",
                    "physicalType": "varchar",
                    "description": "Unique identifier for the clinical trial",
                    "examples": ["CT-12345", "AX-45678"],
                },
                {
                    "name": "enrollment_count",
                    "businessName": "Enrollment Count",
                    "logicalType": "number",
                    "physicalType": "integer",
                    "description": "Number of enrolled patients",
                },
            ],
        },
        {
            "name": "retention_metrics",
            "logicalType": "object",
            "physicalType": "table",
            "physicalName": "clinical-trial-dashboard.retention_metrics",
            "description": "Retention metrics per patient per site",
            "properties": [
                {
                    "name": "trial_id",
                    "logicalType": "string",
                    "physicalType": "varchar",
                },
            ],
        },
    ],
}


def _assign_update_role(session, dataset_id):
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_CONTRACT],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, dataset_id=dataset_id
    )
    return user


class TestContractRouter:
    def test_post_contract(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["output_port_id"] == str(dataset.id)
        assert len(body["schema_objects"]) == 2

        trial_master = body["schema_objects"][0]
        assert trial_master["name"] == "trial_master"
        assert trial_master["physical_type"] == "table"
        assert trial_master["physical_name"] == "clinical-trial-dashboard.trial_master"
        assert trial_master["position"] == 0
        assert len(trial_master["properties"]) == 2

        trial_id_prop = trial_master["properties"][0]
        assert trial_id_prop["name"] == "trial_id"
        assert trial_id_prop["business_name"] == "Trial Identifier"
        assert trial_id_prop["logical_type"] == "string"
        assert trial_id_prop["physical_type"] == "varchar"
        assert trial_id_prop["examples"] == ["CT-12345", "AX-45678"]
        assert trial_id_prop["position"] == 0

    def test_post_contract_no_permissions(self, client):
        dataset = DatasetFactory()

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        assert response.status_code == 403

    def test_post_contract_output_port_not_found(self, client, session):
        dataset = DatasetFactory()
        other_dataset = DatasetFactory()
        _assign_update_role(session, other_dataset.id)

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{other_dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        assert response.status_code == 404

    def test_get_contract_none_existing(self, client, session):
        dataset = DatasetFactory()

        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract"
        )

        assert response.status_code == 404
        data = response.json()
        assert "No schemas found for output port" in data["detail"]

    def test_get_contract_after_ingest(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract"
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["schema_objects"]) == 2
        assert body["schema_objects"][0]["name"] == "trial_master"
        assert body["schema_objects"][1]["name"] == "retention_metrics"

    def test_post_contract_replaces_existing(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        replacement = {
            "schema": [
                {
                    "name": "new_table",
                    "physicalType": "table",
                    "properties": [],
                }
            ]
        }
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=replacement,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["schema_objects"]) == 1
        assert body["schema_objects"][0]["name"] == "new_table"

    def test_post_contract_with_nested_properties(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        payload = {
            "schema": [
                {
                    "name": "orders",
                    "physicalType": "table",
                    "properties": [
                        {
                            "name": "shipping_address",
                            "logicalType": "object",
                            "physicalType": "struct",
                            "properties": [
                                {"name": "street", "logicalType": "string"},
                                {"name": "city", "logicalType": "string"},
                            ],
                        },
                    ],
                }
            ]
        }

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=payload,
        )

        assert response.status_code == 200
        body = response.json()
        props = body["schema_objects"][0]["properties"]
        assert len(props) == 1

        address = next(p for p in props if p["name"] == "shipping_address")
        assert len(address["properties"]) == 2
        nested_names = {p["name"] for p in address["properties"]}
        assert nested_names == {"street", "city"}

    def test_post_contract_property_order_preserved(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        assert response.status_code == 200
        props = response.json()["schema_objects"][0]["properties"]
        assert props[0]["name"] == "trial_id"
        assert props[0]["position"] == 0
        assert props[1]["name"] == "enrollment_count"
        assert props[1]["position"] == 1

    def test_post_contract_empty_schema(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json={"schema": []},
        )

        assert response.status_code == 404
        data = response.json()
        assert "No schemas found for output port" in data["detail"]

    def test_delete_output_port_removes_schema(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset.id)

        client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_contract",
            json=CONTRACT_PAYLOAD,
        )

        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.OUTPUT_PORT__DELETE],
        )
        DatasetRoleAssignmentFactory(
            user_id=UserFactory(external_id=settings.DEFAULT_USERNAME).id,
            role_id=role.id,
            dataset_id=dataset.id,
        )

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}"
        )
        assert response.status_code == 200
