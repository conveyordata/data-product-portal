from app.datasets.enums import DatasetAccessType

ENDPOINT = "/api/datasets"


class TestDatasetsRouter:
    def test_create_dataset(self, client, session, default_dataset):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

    def test_get_datasets(self, client, session, default_dataset):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200

        dataset = client.get(ENDPOINT)
        assert dataset.status_code == 200
        assert len(dataset.json()) == 1

    def test_get_user_datasets(
        self, client, session, default_dataset, default_user_model_payload
    ):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200

        session.add(default_user_model_payload)

        dataset = client.get(f"{ENDPOINT}/user/{default_user_model_payload.id}")
        assert dataset.status_code == 200
        assert len(dataset.json()) == 1

    def test_update_dataset(self, client, session, default_dataset):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        dataset = self.get_dataset_by_id(client, created_dataset.json()["id"])
        assert dataset.status_code == 200
        assert "id" in dataset.json()
        dataset_data = dataset.json()

        updated_dataset = self.update_default_dataset(
            client, session, default_dataset, dataset_data["id"]
        )

        assert updated_dataset.status_code == 200
        assert "id" in updated_dataset.json()

    def test_update_dataset_about(self, client, session, default_dataset, default_user):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        dataset = self.get_dataset_by_id(client, created_dataset.json()["id"])
        assert dataset.status_code == 200
        dataset_data = dataset.json()
        assert "id" in dataset_data

        updated_dataset_about = self.update_dataset_about(client, dataset_data["id"])
        assert updated_dataset_about.status_code == 200

    def test_remove_dataset(self, client, session, default_dataset, default_user):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        dataset_data = created_dataset.json()
        deleted_dataset = self.delete_default_dataset(client, dataset_data["id"])
        assert deleted_dataset.status_code == 200

    def test_remove_user_from_dataset(
        self, client, session, default_dataset, default_user
    ):
        created_dataset = self.create_default_dataset(client, default_dataset)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()
        dataset_id = created_dataset.json()["id"]

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 1

        owner_id = dataset.json()["owners"][0]["id"]

        deleted_dataset = self.delete_dataset_user(client, owner_id, dataset_id)
        assert deleted_dataset.status_code == 200

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 0

    def test_update_dataset_with_invalid_dataset_id(
        self, client, session, default_dataset
    ):
        invalid_dataset_id = "00000000-0000-0000-0000-000000000000"
        dataset = self.update_default_dataset(
            client, session, default_dataset, invalid_dataset_id
        )
        assert dataset.status_code == 404

    @staticmethod
    def default_dataset_payload(default_dataset):
        return {
            "name": default_dataset.name,
            "external_id": default_dataset.external_id,
            "description": default_dataset.description,
            "tags": default_dataset.tags,
            "access_type": default_dataset.access_type,
            "owners": [
                str(default_dataset.owners[0].id),
            ],
            "business_area_id": str(default_dataset.business_area_id),
        }

    @staticmethod
    def default_update_dataset_payload(default_dataset, session):
        session.add(default_dataset)
        return {
            "name": "Updated Dataset Name",
            "description": "Updated Dataset Description",
            "external_id": "Updated Dataset External ID",
            "tags": [
                {"value": "Updated tag"},
            ],
            "owners": [
                str(default_dataset.owners[0].id),
            ],
            "access_type": DatasetAccessType.RESTRICTED,
            "business_area_id": str(default_dataset.business_area_id),
        }

    @staticmethod
    def default_dataset_about_payload():
        return {"about": "Updated Dataset Description"}

    def create_default_dataset(self, client, default_dataset):
        data = self.default_dataset_payload(default_dataset)
        response = client.post(ENDPOINT, json=data)
        return response

    def update_default_dataset(self, client, session, default_dataset, dataset_id):
        data = self.default_update_dataset_payload(default_dataset, session)
        response = client.put(f"{ENDPOINT}/{dataset_id}", json=data)
        return response

    @staticmethod
    def update_dataset_about(client, dataset_id):
        data = TestDatasetsRouter.default_dataset_about_payload()
        response = client.put(f"{ENDPOINT}/{dataset_id}/about", json=data)
        return response

    @staticmethod
    def delete_default_dataset(client, dataset_id):
        response = client.delete(f"{ENDPOINT}/{dataset_id}")
        return response

    @staticmethod
    def get_dataset_by_id(client, dataset_id):
        response = client.get(f"{ENDPOINT}/{dataset_id}")
        return response

    @staticmethod
    def delete_dataset_user(client, user_id, dataset_id):
        response = client.delete(f"{ENDPOINT}/{dataset_id}/user/{user_id}")
        return response
