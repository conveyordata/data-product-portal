import uuid

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    OutputPortSemanticModelFactory,
    RoleFactory,
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


class TestSemanticModelRouter:
    def test_get_semantic_models_empty(self, client, session):
        dataset = DatasetFactory()
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models"
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_semantic_models_returns_existing(self, client, session):
        dataset = DatasetFactory()
        OutputPortSemanticModelFactory(output_port_id=dataset.id, name="revenue_model")
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models"
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body) == 1
        assert body[0]["name"] == "revenue_model"
        assert body[0]["format"] == "MetricsFlow"

    def test_post_creates_semantic_model(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)

        payload = {
            "name": "revenue_model",
            "format": "MetricsFlow",
            "content": {"version": 2, "models": [{"name": "revenue"}]},
        }
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models",
            json=payload,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "revenue_model"
        assert body["format"] == "MetricsFlow"
        assert body["content"]["version"] == 2

    def test_post_requires_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models",
            json={"name": "x", "format": "MetricsFlow", "content": {}},
        )
        assert response.status_code == 403

    def test_put_replaces_semantic_model(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        model = OutputPortSemanticModelFactory(
            output_port_id=dataset.id, name="old_name"
        )

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{model.id}",
            json={
                "name": "new_name",
                "format": "OpenSemanticInterchange",
                "content": {"entities": []},
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "new_name"
        assert body["format"] == "OpenSemanticInterchange"

    def test_put_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{uuid.uuid4()}",
            json={"name": "x", "format": "MetricsFlow", "content": {}},
        )
        assert response.status_code == 404

    def test_delete_removes_semantic_model(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        model = OutputPortSemanticModelFactory(output_port_id=dataset.id)

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{model.id}"
        )
        assert response.status_code == 204

    def test_delete_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/semantic-models/{uuid.uuid4()}"
        )
        assert response.status_code == 404
