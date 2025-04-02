import uuid
from copy import deepcopy

import pytest
from tests.factories import DatasetFactory, DomainFactory, UserFactory
from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.data_product_setting import DataProductSettingFactory
from tests.factories.data_products_datasets import DataProductDatasetAssociationFactory

from app.core.namespace.validation import NamespaceValidityType
from app.datasets.enums import DatasetAccessType

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

    def test_create_dataset(self, dataset_payload, client):
        created_dataset = self.create_default_dataset(client, dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

    def test_create_dataset_no_owners(self, dataset_payload, client):
        create_payload = deepcopy(dataset_payload)
        create_payload["owners"] = []
        created_dataset = self.create_default_dataset(client, create_payload)
        assert created_dataset.status_code == 422

    def test_create_dataset_duplicate_namespace(self, dataset_payload, client):
        DatasetFactory(namespace=dataset_payload["namespace"])

        created_dataset = self.create_default_dataset(client, dataset_payload)
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_characters_namespace(self, dataset_payload, client):
        create_payload = deepcopy(dataset_payload)
        create_payload["namespace"] = "!"

        created_dataset = self.create_default_dataset(client, create_payload)
        assert created_dataset.status_code == 400

    def test_create_dataset_invalid_length_namespace(self, dataset_payload, client):
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
        assert data[0]["owners"][0]["id"] == str(ds.owners[0].id)

    def test_get_user_datasets(self, client):
        user_1, user_2 = UserFactory.create_batch(2)
        DatasetFactory(owners=[user_1])
        ds = DatasetFactory(owners=[user_1, user_2])

        response = client.get(f"{ENDPOINT}/user/{user_2.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert len(data[0]["owners"]) == 2
        assert str(user_2.id) in [owner["id"] for owner in data[0]["owners"]]
        assert data[0]["id"] == str(ds.id)

    def test_update_dataset_not_owner(self, client):
        ds = DatasetFactory()
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "owners": [str(ds.owners[0].id)],
            "domain_id": str(ds.domain_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 403

    def test_update_dataset(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tag_ids": [],
            "access_type": "public",
            "owners": [str(ds.owners[0].id)],
            "domain_id": str(ds.domain_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 200
        assert updated_dataset.json()["id"] == str(ds.id)

    def test_update_dataset_remove_all_owners(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "owners": [],
            "domain_id": str(ds.domain_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 422

    def test_update_dataset_about_not_owners(self, client):
        ds = DatasetFactory()
        response = self.update_dataset_about(client, ds.id)
        assert response.status_code == 403

    def test_update_dataset_about(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        response = self.update_dataset_about(client, ds.id)
        assert response.status_code == 200

    def test_remove_dataset_not_owner(self, client):
        ds = DatasetFactory()
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 403

    def test_remove_dataset(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        response = self.delete_default_dataset(client, ds.id)
        assert response.status_code == 200

        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 404

    def test_add_user_to_dataset(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        user = UserFactory()
        response = self.add_user_to_dataset(client, user.id, ds.id)
        assert response.status_code == 200

        dataset = self.get_dataset_by_id(client, ds.id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 2

    def test_add_user_to_dataset_by_admin(self, client):
        # Create admin user which is used as logged in user
        UserFactory(external_id="sub", is_admin=True)
        # Add dataset which is owned by another non-admin user
        ds = DatasetFactory(owners=[UserFactory()])
        # Create one more user that should be added to the dataset by admin user
        new_user = UserFactory()
        response = self.add_user_to_dataset(client, new_user.id, ds.id)
        assert response.status_code == 200

        dataset = self.get_dataset_by_id(client, ds.id)
        data = dataset.json()
        assert len(data["owners"]) == 2
        assert str(new_user.id) in [owner["id"] for owner in data["owners"]]

    def test_remove_user_from_dataset(self, client):
        ds_owner = UserFactory()
        # Create dataset with two owners
        ds = DatasetFactory(owners=[ds_owner, UserFactory(external_id="sub")])

        response = self.delete_dataset_user(client, ds_owner.id, ds.id)
        assert response.status_code == 200

        dataset = self.get_dataset_by_id(client, ds.id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 1

    def test_remove_last_user_from_dataset(self, client):
        owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[owner])

        response = self.delete_dataset_user(client, owner.id, ds.id)
        assert response.status_code == 400

    def test_get_dataset_by_id_with_invalid_dataset_id(self, client, session):
        dataset = self.get_dataset_by_id(client, self.invalid_id)
        assert dataset.status_code == 404

    def test_update_dataset_with_invalid_dataset_id(self, client):
        update_payload = {
            "name": "new_name",
            "namespace": "new_namespace",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "owners": [],
            "domain_id": str(uuid.uuid4()),
        }
        dataset = self.update_default_dataset(client, update_payload, self.invalid_id)
        assert dataset.status_code == 404

    def test_remove_dataset_with_invalid_dataset_id(self, client):
        dataset = self.delete_default_dataset(client, self.invalid_id)
        assert dataset.status_code == 404

    def test_remove_user_from_dataset_with_invalid_dataset_id(self, client):
        user = UserFactory()
        dataset = self.delete_dataset_user(client, user.id, self.invalid_id)
        assert dataset.status_code == 404

    def test_remove_user_from_dataset_with_invalid_user_id(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        response = self.delete_dataset_user(client, self.invalid_id, ds.id)
        assert response.status_code == 404

    def test_add_already_existing_dataset_owner_to_dataset(self, client):
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[ds_owner])

        response = self.add_user_to_dataset(client, ds_owner.id, ds.id)
        assert response.status_code == 400
        assert "is already an owner of dataset" in response.json()["detail"]

    def test_update_status_not_owner(self, client):
        ds = DatasetFactory()
        response = self.update_dataset_status(client, {"status": "active"}, ds.id)
        assert response.status_code == 403

    def test_update_status(self, client):
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[ds_owner])
        response = self.get_dataset_by_id(client, ds.id)
        assert response.json()["status"] == "active"
        response = self.update_dataset_status(client, {"status": "pending"}, ds.id)
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

    def test_dataset_set_custom_setting_wrong_scope(self, client):
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[ds_owner])
        ds = DatasetFactory()
        setting = DataProductSettingFactory()
        response = client.post(f"{ENDPOINT}/{ds.id}/settings/{setting.id}")
        assert response.status_code == 403

    def test_dataset_set_custom_setting_not_owner(self, client):
        ds = DatasetFactory()
        setting = DataProductSettingFactory(scope="dataset")
        response = client.post(f"{ENDPOINT}/{ds.id}/settings/{setting.id}")
        assert response.status_code == 403

    def test_dataset_set_custom_setting(self, client):
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(owners=[ds_owner])
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
        ds_owner = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE, owners=[ds_owner])
        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_get_private_dataset_by_admin(self, client):
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 200

    def test_get_private_dataset_by_member_of_consuming_data_product(self, client):
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductMembershipFactory(user=user).data_product
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)

        response = self.get_dataset_by_id(client, ds.id)
        assert response.status_code == 200

    def test_get_private_datasets_not_allowed(self, client):
        DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_private_datasets_by_owner(self, client):
        ds_owner = UserFactory(external_id="sub")
        DatasetFactory(access_type=DatasetAccessType.PRIVATE, owners=[ds_owner])
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
        user = UserFactory(external_id="sub")
        ds = DatasetFactory(access_type=DatasetAccessType.PRIVATE)
        dp = DataProductMembershipFactory(user=user).data_product
        DataProductDatasetAssociationFactory(data_product=dp, dataset=ds)

        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_namespace_suggestion_subsitution(self, client):
        name = "test with spaces"
        response = self.get_namespace_suggestion(client, name)
        body = response.json()

        assert response.status_code == 200
        assert body["namespace"] == "test-with-spaces"
        assert body["available"] is True

    def test_get_namespace_suggestion_not_available(self, client):
        namespace = "test"
        DatasetFactory(namespace=namespace)
        response = self.get_namespace_suggestion(client, namespace)
        body = response.json()
        assert response.status_code == 200
        assert body["namespace"] == namespace
        assert body["available"] is False

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
    def delete_dataset_user(client, user_id, dataset_id):
        return client.delete(f"{ENDPOINT}/{dataset_id}/user/{user_id}")

    @staticmethod
    def add_user_to_dataset(client, user_id, dataset_id):
        return client.post(f"{ENDPOINT}/{dataset_id}/user/{user_id}")

    @staticmethod
    def get_namespace_suggestion(client, name):
        return client.get(f"{ENDPOINT}/namespace_suggestion?name={name}")

    @staticmethod
    def validate_namespace(client, namespace):
        return client.get(f"{ENDPOINT}/validate_namespace?namespace={namespace}")

    @staticmethod
    def get_namespace_length_limits(client):
        return client.get(f"{ENDPOINT}/namespace_length_limits")
