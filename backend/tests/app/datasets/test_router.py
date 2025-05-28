import uuid
from copy import deepcopy

import pytest
from tests.factories import (
    DataProductDatasetAssociationFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DataProductSettingFactory,
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    GlobalRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

from app.core.authz.actions import AuthorizationAction
from app.core.namespace.validation import NamespaceValidityType
from app.datasets.enums import DatasetAccessType
from app.roles.schema import Prototype, Scope
from app.roles.service import RoleService

ENDPOINT = "/api/datasets"


@pytest.fixture
def dataset_payload():
    user = UserFactory()
    domain = DomainFactory()
    return {
        "name": "Test Dataset",
        "description": "Test Description",
        "namespace": "test-dataset",
        "tag_ids": [],
        "owners": [
            str(user.id),
        ],
        "access_type": DatasetAccessType.RESTRICTED.value,
        "domain_id": str(domain.id),
    }


class TestDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_dataset(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_DATASET]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_dataset = self.create_default_dataset(client, dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

    def test_create_dataset_no_owner_role(self, dataset_payload, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_DATASET]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        created_dataset = self.create_default_dataset(client, dataset_payload)
        assert created_dataset.status_code == 400

    def test_create_dataset_no_owners(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_DATASET]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        create_payload = deepcopy(dataset_payload)
        create_payload["owners"] = []
        created_dataset = self.create_default_dataset(client, create_payload)
        assert created_dataset.status_code == 422

    def test_create_dataset_duplicate_namespace(self, session, dataset_payload, client):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_DATASET]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        DatasetFactory(namespace=dataset_payload["namespace"])

        created_dataset = self.create_default_dataset(client, dataset_payload)
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_characters_namespace(
        self, session, dataset_payload, client
    ):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_DATASET]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        create_payload = deepcopy(dataset_payload)
        create_payload["namespace"] = "!"

        created_dataset = self.create_default_dataset(client, create_payload)
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_length_namespace(
        self, session, dataset_payload, client
    ):
        RoleService(db=session).initialize_prototype_roles()
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_DATASET]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        create_payload = deepcopy(dataset_payload)
        create_payload["namespace"] = "a" * 256

        created_dataset = self.create_default_dataset(client, create_payload)
        assert created_dataset.status_code == 400

    def test_get_datasets(self, client):
        ds = DatasetFactory()
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(ds.id)

    def test_get_user_datasets(self, client):
        user_1, user_2 = UserFactory.create_batch(2)
        ds_1, ds_2 = DatasetFactory.create_batch(2)
        owner = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        DatasetRoleAssignmentFactory(
            dataset_id=ds_1.id, user_id=user_1.id, role_id=owner.id
        )
        DatasetRoleAssignmentFactory(
            dataset_id=ds_2.id, user_id=user_2.id, role_id=owner.id
        )

        response = client.get(f"{ENDPOINT}/user/{user_2.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(ds_2.id)

    def test_update_dataset_no_role(self, client):
        ds = DatasetFactory()
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "domain_id": str(ds.domain_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 403

    def test_update_dataset(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
            "domain_id": str(ds.domain_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 200
        assert updated_dataset.json()["id"] == str(ds.id)

    def test_update_dataset_about_no_role(self, client):
        ds = DatasetFactory()
        response = self.update_dataset_about(client, ds.id)
        assert response.status_code == 403

    def test_update_dataset_about(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.update_dataset_about(client, ds.id)
        assert response.status_code == 200

    def test_remove_dataset_not_owner(self, client):
        ds = DatasetFactory()
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 403

    def test_remove_dataset(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.DATASET__DELETE]
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 200

        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 404

    def test_get_dataset_by_id_with_invalid_dataset_id(self, client, session):
        dataset = self.get_dataset_by_id(client, self.invalid_id)
        assert dataset.status_code == 404

    def test_update_dataset_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "domain_id": str(uuid.uuid4()),
        }
        dataset = self.update_default_dataset(client, update_payload, self.invalid_id)
        assert dataset.status_code == 403

    def test_remove_dataset_with_invalid_dataset_id(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET, permissions=[AuthorizationAction.DATASET__DELETE]
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        dataset = self.delete_default_dataset(client, self.invalid_id)
        assert dataset.status_code == 403

    def test_update_status_no_role(self, client):
        ds = DatasetFactory()
        response = self.update_dataset_status(client, {"status": "active"}, ds.id)
        assert response.status_code == 403

    def test_update_status(self, client):
        ds_owner = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__UPDATE_STATUS],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(
            user_id=ds_owner.id, role_id=role.id, dataset_id=ds.id
        )
        response = self.get_dataset_by_id(client, ds.id)
        assert response.json()["status"] == "active"
        response = self.update_dataset_status(client, {"status": "pending"}, ds.id)
        assert response.status_code == 200
        response = self.get_dataset_by_id(client, ds.id)
        assert response.json()["status"] == "pending"

    def test_get_graph_data(self, client):
        ds = DatasetFactory()
        response = client.get(f"{ENDPOINT}/{ds.id}/graph")
        assert response.json() == {
            "edges": [],
            "nodes": [
                {
                    "data": {
                        "icon_key": None,
                        "id": str(ds.id),
                        "link_to_id": None,
                        "name": ds.name,
                    },
                    "id": str(ds.id),
                    "isMain": True,
                    "type": "datasetNode",
                }
            ],
        }

    def test_dataset_set_custom_setting_no_role(self, client):
        ds = DatasetFactory()
        setting = DataProductSettingFactory(scope="dataset")
        response = client.post(f"{ENDPOINT}/{ds.id}/settings/{setting.id}")
        assert response.status_code == 403

    def test_dataset_set_custom_setting(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__UPDATE_SETTINGS],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        setting = DataProductSettingFactory(scope="dataset")

        response = client.post(f"{ENDPOINT}/{ds.id}/settings/{setting.id}?value=false")
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT}/{ds.id}")
        assert response.json()["data_product_settings"][0]["value"] == "false"

    def test_get_private_dataset_not_allowed(self, client):
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 403

    def test_get_private_dataset_by_owner(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(scope=Scope.DATASET, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_get_private_dataset_by_admin(self, client):
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 200

    def test_get_private_dataset_by_member_of_consuming_data_product(self, client):
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductFactory()
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)
        user = UserFactory(external_id="sub")
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            data_product_id=dp.id, user_id=user.id, role_id=role.id
        )

        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 200

    def test_get_private_datasets_not_allowed(self, client):
        DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_private_datasets_by_owner(self, client):
        user = UserFactory(external_id="sub")
        role = RoleFactory(scope=Scope.DATA_PRODUCT, prototype=Prototype.OWNER)
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_get_private_datasets_by_admin(self, client):
        DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_private_datasets_by_member_of_consuming_data_product(self, client):
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductFactory()
        user = UserFactory(external_id="sub")
        role = RoleFactory(scope=Scope.DATA_PRODUCT)
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=dp.id
        )
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 1

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
        assert response.json()["validity"] == NamespaceValidityType.VALID.value

    def test_validate_namespace_invalid_characters(self, client):
        namespace = "!"
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert (
            response.json()["validity"]
            == NamespaceValidityType.INVALID_CHARACTERS.value
        )

    def test_validate_namespace_invalid_length(self, client):
        namespace = "a" * 256
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert response.json()["validity"] == NamespaceValidityType.INVALID_LENGTH.value

    def test_validate_namespace_duplicate(self, client):
        namespace = "test"
        DatasetFactory(namespace=namespace)
        response = self.validate_namespace(client, namespace)
        assert response.status_code == 200
        assert (
            response.json()["validity"]
            == NamespaceValidityType.DUPLICATE_NAMESPACE.value
        )

    def test_update_dataset_duplicate_namespace(self, client):
        namespace = "namespace"
        DatasetFactory(namespace=namespace)
        user = UserFactory(external_id="sub")
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__UPDATE_PROPERTIES],
        )
        ds = DatasetFactory()
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)
        update_payload = {
            "name": "new_name",
            "namespace": namespace,
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
            "domain_id": str(ds.domain_id),
        }

        response = self.update_default_dataset(client, update_payload, ds.id)

        assert response.status_code == 400

    @staticmethod
    def create_default_dataset(client, default_dataset_payload):
        return client.post(ENDPOINT, json=default_dataset_payload)

    @staticmethod
    def update_dataset_status(client, status, dataset_id):
        return client.put(f"{ENDPOINT}/{dataset_id}/status", json=status)

    @staticmethod
    def update_default_dataset(client, default_dataset_payload, dataset_id):
        return client.put(f"{ENDPOINT}/{dataset_id}", json=default_dataset_payload)

    @staticmethod
    def update_dataset_about(client, dataset_id):
        data = {"about": "Updated Dataset Description"}
        return client.put(f"{ENDPOINT}/{dataset_id}/about", json=data)

    @staticmethod
    def delete_default_dataset(client, dataset_id):
        return client.delete(f"{ENDPOINT}/{dataset_id}")

    @staticmethod
    def get_dataset_by_id(client, dataset_id):
        return client.get(f"{ENDPOINT}/{dataset_id}")

    @staticmethod
    def get_namespace_suggestion(client, name):
        return client.get(f"{ENDPOINT}/namespace_suggestion?name={name}")

    @staticmethod
    def validate_namespace(client, namespace):
        return client.get(f"{ENDPOINT}/validate_namespace?namespace={namespace}")

    @staticmethod
    def get_namespace_length_limits(client):
        return client.get(f"{ENDPOINT}/namespace_length_limits")
