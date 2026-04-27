import uuid

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    OutputPortTableSchemaFactory,
    RoleFactory,
    TagFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


def _assign_update_properties_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, dataset_id=dataset.id
    )
    return user


class TestTableSchemaRouter:
    def test_get_table_schemas_empty(self, client, session):
        dataset = DatasetFactory()
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas"
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_table_schemas_returns_existing(self, client, session):
        dataset = DatasetFactory()
        OutputPortTableSchemaFactory(output_port_id=dataset.id, name="orders")
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas"
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["name"] == "orders"
        assert body[0]["columns"] == []
        assert body[0]["tags"] == []

    def test_post_creates_table_schema_with_columns(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        tag = TagFactory()

        payload = {
            "name": "orders",
            "description": "Order transactions",
            "tag_ids": [str(tag.id)],
            "columns": [
                {"name": "id", "data_type": "int", "description": "PK", "tag_ids": []},
                {
                    "name": "amount",
                    "data_type": "decimal",
                    "description": "Total",
                    "tag_ids": [],
                },
            ],
        }
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas",
            json=payload,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "orders"
        assert len(body["columns"]) == 2
        assert body["columns"][0]["name"] == "amount"  # sorted alphabetically
        assert len(body["tags"]) == 1
        assert body["tags"][0]["id"] == str(tag.id)

    def test_post_requires_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas",
            json={"name": "orders", "tag_ids": [], "columns": []},
        )
        assert response.status_code == 403

    def test_put_replaces_table_schema(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        schema = OutputPortTableSchemaFactory(
            output_port_id=dataset.id, name="old_name"
        )

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{schema.id}",
            json={"name": "new_name", "tag_ids": [], "columns": []},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "new_name"

    def test_put_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{uuid.uuid4()}",
            json={"name": "x", "tag_ids": [], "columns": []},
        )
        assert response.status_code == 404

    def test_delete_removes_table_schema(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        schema = OutputPortTableSchemaFactory(output_port_id=dataset.id)

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{schema.id}"
        )
        assert response.status_code == 204

    def test_delete_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/table-schemas/{uuid.uuid4()}"
        )
        assert response.status_code == 404
