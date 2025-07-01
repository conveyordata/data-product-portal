import json
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from tests.factories import (
    DataOutputFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DataProductSettingFactory,
    DataProductTypeFactory,
    DomainFactory,
    EnvironmentFactory,
    EnvPlatformConfigFactory,
    GlobalRoleAssignmentFactory,
    LifecycleFactory,
    PlatformFactory,
    RoleFactory,
    TagFactory,
    UserFactory,
)

from app.core.authz import Action
from app.core.namespace.validation import NamespaceValidityType
from app.roles.schema import Scope
from app.roles.service import RoleService

ENDPOINT = "/api/data_products"


@pytest.fixture
def payload():
    domain = DomainFactory()
    lifecycle = LifecycleFactory()
    data_product_type = DataProductTypeFactory()
    user = UserFactory()
    tag = TagFactory()
    return {
        "name": "Data Product Name",
        "description": "Updated Data Product Description",
        "namespace": "namespace",
        "tag_ids": [str(tag.id)],
        "type_id": str(data_product_type.id),
        "owners": [str(user.id)],
        "lifecycle_id": str(lifecycle.id),
        "domain_id": str(domain.id),
    }


class TestDataProductsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_data_product(self, payload, client, session):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

    def test_create_data_product_no_owner_role(self, payload, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 400

    def test_create_data_product_no_owners(self, session, payload, client):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        create_payload = deepcopy(payload)
        create_payload["owners"] = []
        created_data_product = self.create_data_product(client, create_payload)
        assert created_data_product.status_code == 422

    def test_create_data_product_duplicate_namespace(self, session, payload, client):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        DataProductFactory(namespace=payload["namespace"])

        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 400

    def test_create_data_product_invalid_characters_namespace(
        self, session, payload, client
    ):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        create_payload = deepcopy(payload)
        create_payload["namespace"] = "!"

        created_data_product = self.create_data_product(client, create_payload)
        assert created_data_product.status_code == 400

    def test_create_data_product_invalid_length_namespace(
        self, session, payload, client
    ):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )

        create_payload = deepcopy(payload)
        create_payload["namespace"] = "a" * 256

        created_data_product = self.create_data_product(client, create_payload)
        assert created_data_product.status_code == 400

    def test_get_data_products(self, client):
        data_product = DataProductFactory()
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(data_product.id)

    def test_get_data_product_by_id(self, client):
        data_product = DataProductFactory()

        response = self.get_data_product_by_id(client, data_product.id)
        assert response.status_code == 200
        assert response.json()["id"] == str(data_product.id)

    def test_get_conveyor_ide_url(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )

        response = self.get_conveyor_ide_url(client, data_product.id)
        assert response.status_code == 501

    def test_get_data_product_by_user_id(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=RoleFactory().id,
        )

        response = self.get_data_product_by_user_id(client, user.id)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(data_product.id)

    def test_get_data_outputs(self, client):
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        response = self.get_data_outputs(client, data_product.id)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(data_output.id)

    def test_update_data_product_no_member(self, payload, client):
        data_product = DataProductFactory()
        update_payload = deepcopy(payload)
        update_payload["name"] = "Updated Data Product"
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 403

    def test_update_data_product(self, payload, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        update_payload = deepcopy(payload)
        update_payload["name"] = "Updated Data Product"
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 200
        assert response.json()["id"] == str(data_product.id)

    def test_update_data_product_about_no_member(self, client):
        data_product = DataProductFactory()
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 403

    def test_update_data_product_about(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 200

    def test_remove_data_product_no_member(self, client):
        data_product = DataProductFactory()
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 403

    def test_remove_data_product(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

    def test_update_status_not_owner(self, client):
        data_product = DataProductFactory()
        response = self.update_data_product_status(
            client, {"status": "active"}, data_product.id
        )
        assert response.status_code == 403

    def test_update_status(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_STATUS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = self.get_data_product_by_id(client, data_product.id)
        assert response.json()["status"] == "pending"
        _ = self.update_data_product_status(
            client, {"status": "active"}, data_product.id
        )
        response = self.get_data_product_by_id(client, data_product.id)
        assert response.json()["status"] == "active"

    def test_get_data_product_by_id_with_invalid_id(self, client):
        data_product = self.get_data_product_by_id(client, self.invalid_id)
        assert data_product.status_code == 404

    def test_update_data_product_with_invalid_data_product_id(self, client, payload):
        data_product = self.update_data_product(client, payload, self.invalid_id)
        assert data_product.status_code == 403

    def test_remove_data_product_with_invalid_data_product_id(self, client):
        data_product = self.delete_data_product(client, self.invalid_id)
        assert data_product.status_code == 403

    def test_data_product_set_custom_setting_wrong_scope(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_SETTINGS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        setting = DataProductSettingFactory(scope="dataset")
        with pytest.raises(IntegrityError):
            client.post(
                f"{ENDPOINT}/{data_product.id}/settings/{setting.id}?value=false"
            )

    def test_dataset_set_custom_setting_not_owner(self, client):
        data_product = DataProductFactory()
        setting = DataProductSettingFactory()
        response = client.post(f"{ENDPOINT}/{data_product.id}/settings/{setting.id}")
        assert response.status_code == 403

    def test_dataset_set_custom_setting(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_SETTINGS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        setting = DataProductSettingFactory()
        response = client.post(
            f"{ENDPOINT}/{data_product.id}/settings/{setting.id}?value=false"
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT}/{data_product.id}")
        assert response.json()["data_product_settings"][0]["value"] == "false"

    def test_get_graph_data(self, client):
        data_product = DataProductFactory()
        response = client.get(f"{ENDPOINT}/{data_product.id}/graph")
        assert response.json()["edges"] == []
        for node in response.json()["nodes"]:
            assert node == {
                "data": {
                    "icon_key": "default",
                    "id": str(data_product.id),
                    "link_to_id": None,
                    "name": data_product.name,
                    "domain": None,
                    "domain_id": None,
                    "assignments": None,
                    "description": None,
                },
                "id": str(data_product.id),
                "isMain": True,
                "type": "dataProductNode",
            }

    def test_get_aws_role_not_member(self, client):
        data_product = DataProductFactory()
        response = client.get(f"{ENDPOINT}/{data_product.id}/role")
        assert response.status_code == 403

    def test_get_aws_role(self, client):
        env = EnvironmentFactory(name="production")
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/role?environment=production"
        )
        assert response.status_code == 200
        assert response.json() == env.context.replace("{{}}", data_product.namespace)

    def test_get_signin_url_not_implemented(self, client):
        EnvironmentFactory(name="production")
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/integration_url?"
            "integration_type=aws&environment=production"
        )
        assert (
            response.status_code == 501 or response.status_code == 400
        )  # TODO Add actual AWS test through mocking

    def test_get_databricks_url(self, client):
        env = EnvironmentFactory(name="production")
        platform = PlatformFactory(name="Databricks")
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        EnvPlatformConfigFactory(
            environment=env,
            platform=platform,
            config=json.dumps(
                {"workspace_urls": {str(data_product.domain.id): "test_1.com"}}
            ),
        )
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/integration_url?integration_type=databricks&"
            "environment=production"
        )
        assert response.status_code == 200
        assert response.json() == "test_1.com"

    def test_get_snowflake_url(self, client):
        env = EnvironmentFactory(name="production")
        platform = PlatformFactory(name="Snowflake")
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__READ_INTEGRATIONS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        EnvPlatformConfigFactory(
            environment=env,
            platform=platform,
            config=json.dumps({"login_url": "test_1.com"}),
        )
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/integration_url?integration_type=snowflake&"
            "environment=production"
        )
        assert response.status_code == 200
        assert response.json() == "test_1.com"

    def test_get_namespace_suggestion_substitution(self, client):
        name = "test with spaces"
        response = self.get_namespace_suggestion(client, name)
        body = response.json()

        assert response.status_code == 200
        assert body["namespace"] == "test-with-spaces"

    def test_get_namespace_length_limits(self, client):
        response = self.get_namespace_length_limits(client)
        assert response.status_code == 200
        assert response.json()["max_length"] > 1

    def test_validate_namespace(self, client):
        namespace = "test"
        response = self.validate_namespace(client, namespace)

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.VALID

    def test_validate_namespace_invalid_characters(self, client):
        namespace = "!"
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_CHARACTERS

    def test_validate_namespace_invalid_length(self, client):
        namespace = "a" * 256
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_LENGTH

    def test_validate_namespace_duplicate(self, client):
        namespace = "test"
        DataProductFactory(namespace=namespace)
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.DUPLICATE_NAMESPACE

    def test_validate_data_output_namespace(self, client):
        namespace = "test"
        data_product = DataProductFactory()
        response = self.validate_data_output_namespace(
            client, namespace, data_product.id
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.VALID

    def test_validate_data_output_namespace_invalid_characters(self, client):
        namespace = "!"
        data_product = DataProductFactory()
        response = self.validate_data_output_namespace(
            client, namespace, data_product.id
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_CHARACTERS

    def test_validate_data_output_namespace_invalid_length(self, client):
        namespace = "a" * 256
        data_product = DataProductFactory()
        response = self.validate_data_output_namespace(
            client, namespace, data_product.id
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_LENGTH

    def test_validate_data_output_namespace_duplicate(self, client):
        namespace = "test"
        data_product = DataProductFactory()
        DataOutputFactory(owner=data_product, namespace=namespace)
        response = self.validate_data_output_namespace(
            client, namespace, data_product.id
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.DUPLICATE_NAMESPACE

    def test_validate_data_output_namespace_duplicate_scoped_to_data_product(
        self, client: TestClient
    ):
        namespace = "test"
        data_product = DataProductFactory()
        other_data_product = DataProductFactory()
        DataOutputFactory(owner=data_product, namespace=namespace)
        response = self.validate_data_output_namespace(
            client, namespace, other_data_product.id
        )

        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.VALID

    def test_update_data_product_duplicate_namespace(self, payload, client: TestClient):
        namespace = "namespace"
        DataProductFactory(namespace=namespace)
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        update_payload = deepcopy(payload)
        update_payload["namespace"] = namespace
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 400

    def test_history_event_created_on_data_product_creation(
        self, payload, client: TestClient, session
    ):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL,
            permissions=[Action.GLOBAL__CREATE_DATAPRODUCT],
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

        history = self.get_data_product_history(
            client, created_data_product.json().get("id")
        ).json()
        assert len(history) == 2

    def test_history_event_created_on_data_product_update(
        self, payload, client: TestClient
    ):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        update_payload = deepcopy(payload)
        update_payload["name"] = "Updated Data Product"
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 1

    def test_history_event_created_on_data_product_about_update(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 1

    def test_history_event_created_on_data_product_status_update(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_STATUS],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )

        response = self.update_data_product_status(
            client, {"status": "active"}, data_product.id
        )
        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 1

    def test_history_event_created_on_data_product_deletion(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

        history = self.get_data_product_history(client, data_product.id).json()
        assert len(history) == 1

    def test_retain_deleted_data_product_name_in_history(self, client: TestClient):
        user = UserFactory(external_id="sub")
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )

        data_product_id = data_product.id
        data_product_name = data_product.name

        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

        response = self.get_data_product_history(client, data_product_id)
        assert len(response.json()) == 1
        assert response.json()[0]["deleted_subject_identifier"] == data_product_name

    @staticmethod
    def create_data_product(client: TestClient, default_data_product_payload):
        return client.post(ENDPOINT, json=default_data_product_payload)

    @staticmethod
    def update_data_product(client: TestClient, payload, data_product_id):
        return client.put(f"{ENDPOINT}/{data_product_id}", json=payload)

    @staticmethod
    def update_data_product_about(client: TestClient, data_product_id):
        data = {"about": "Updated Data Product Description"}
        return client.put(f"{ENDPOINT}/{data_product_id}/about", json=data)

    @staticmethod
    def update_data_product_status(client: TestClient, status, data_product_id):
        return client.put(f"{ENDPOINT}/{data_product_id}/status", json=status)

    @staticmethod
    def delete_data_product(client: TestClient, data_product_id):
        return client.delete(f"{ENDPOINT}/{data_product_id}")

    @staticmethod
    def get_data_product_by_id(client: TestClient, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}")

    @staticmethod
    def get_data_outputs(client: TestClient, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}/data_outputs")

    @staticmethod
    def get_data_product_by_user_id(client: TestClient, user_id):
        return client.get(f"{ENDPOINT}/user/{user_id}")

    @staticmethod
    def get_data_product_history(client: TestClient, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}/history")

    @staticmethod
    def get_conveyor_ide_url(client: TestClient, data_product_id):
        return client.get(
            f"{ENDPOINT}/{data_product_id}/integration_url?"
            "integration_type=conveyor&environment=default"
        )

    @staticmethod
    def get_namespace_suggestion(client: TestClient, name):
        return client.get(f"{ENDPOINT}/namespace_suggestion?name={name}")

    @staticmethod
    def validate_namespace(client: TestClient, namespace):
        return client.get(f"{ENDPOINT}/validate_namespace?namespace={namespace}")

    @staticmethod
    def get_namespace_length_limits(client: TestClient):
        return client.get(f"{ENDPOINT}/namespace_length_limits")

    @staticmethod
    def validate_data_output_namespace(client: TestClient, namespace, data_product_id):
        return client.get(
            f"{ENDPOINT}/{data_product_id}/data_output"
            f"/validate_namespace?namespace={namespace}"
        )
