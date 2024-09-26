import uuid

import pytest
from tests.factories import BusinessAreaFactory, DatasetFactory, UserFactory

from app.datasets.enums import DatasetAccessType

ENDPOINT = "/api/datasets"


@pytest.fixture
def dataset_payload():
    user = UserFactory()
    business_area = BusinessAreaFactory()
    return {
        "name": "Test Dataset",
        "description": "Test Description",
        "external_id": "test-dataset",
        "tags": [],
        "owners": [
            str(user.id),
        ],
        "access_type": DatasetAccessType.RESTRICTED.value,
        "business_area_id": str(business_area.id),
    }


class TestDatasetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_dataset(self, dataset_payload, client):
        created_dataset = self.create_default_dataset(client, dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

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
            "external_id": "new_external_id",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "owners": [str(ds.owners[0].id)],
            "business_area_id": str(ds.business_area_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 403

    def test_update_dataset(self, client):
        ds = DatasetFactory(owners=[UserFactory(external_id="sub")])
        update_payload = {
            "name": "new_name",
            "external_id": "new_external_id",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "owners": [str(ds.owners[0].id)],
            "business_area_id": str(ds.business_area_id),
        }

        updated_dataset = self.update_default_dataset(client, update_payload, ds.id)

        assert updated_dataset.status_code == 200
        assert updated_dataset.json()["id"] == str(ds.id)

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

    def test_get_dataset_by_id_with_invalid_dataset_id(self, client, session):
        dataset = self.get_dataset_by_id(client, self.invalid_id)
        assert dataset.status_code == 404

    def test_update_dataset_with_invalid_dataset_id(self, client):
        update_payload = {
            "name": "new_name",
            "external_id": "new_external_id",
            "description": "new_description",
            "tags": [],
            "access_type": "public",
            "owners": [],
            "business_area_id": str(uuid.uuid4()),
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

    @staticmethod
    def create_default_dataset(client, default_dataset_payload):
        return client.post(ENDPOINT, json=default_dataset_payload)

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
