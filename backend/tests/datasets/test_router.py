ENDPOINT = "/api/datasets"


class TestDatasetsRouter:
    invalid_dataset_id = "00000000-0000-0000-0000-000000000000"

    def test_create_dataset(self, client, session, default_dataset_payload):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

    def test_get_datasets(self, client, session, default_dataset_payload):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200

        dataset = client.get(ENDPOINT)
        assert dataset.status_code == 200
        assert len(dataset.json()) == 1

    def test_get_user_datasets(
        self, client, session, default_dataset_payload, default_user_model_payload
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200

        session.add(default_user_model_payload)

        dataset = client.get(f"{ENDPOINT}/user/{default_user_model_payload.id}")
        assert dataset.status_code == 200
        assert len(dataset.json()) == 1

    def test_update_dataset(self, client, session, default_dataset_payload):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        dataset = self.get_dataset_by_id(client, created_dataset.json()["id"])
        assert dataset.status_code == 200
        assert "id" in dataset.json()
        dataset_data = dataset.json()

        updated_dataset = self.update_default_dataset(
            client, default_dataset_payload, dataset_data["id"]
        )

        assert updated_dataset.status_code == 200
        assert "id" in updated_dataset.json()

    def test_update_dataset_about(
        self, client, session, default_dataset_payload, default_user
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        dataset = self.get_dataset_by_id(client, created_dataset.json()["id"])
        assert dataset.status_code == 200
        dataset_data = dataset.json()
        assert "id" in dataset_data

        updated_dataset_about = self.update_dataset_about(client, dataset_data["id"])
        assert updated_dataset_about.status_code == 200

    def test_remove_dataset(
        self, client, session, default_dataset_payload, default_user
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        dataset_data = created_dataset.json()
        deleted_dataset = self.delete_default_dataset(client, dataset_data["id"])
        assert deleted_dataset.status_code == 200

    def test_add_user_to_dataset(
        self,
        client,
        session,
        default_dataset_payload,
        default_user,
        default_secondary_user,
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()

        session.add(default_secondary_user)

        dataset_id = created_dataset.json()["id"]
        user_id = default_secondary_user.id

        add_user_to_dataset_response = self.add_user_to_dataset(
            client, user_id, dataset_id
        )
        assert add_user_to_dataset_response.status_code == 200

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 2

    def test_remove_user_from_dataset(
        self, client, session, default_dataset_payload, default_user
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()
        dataset_id = created_dataset.json()["id"]

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 1

        owner_id = dataset.json()["owners"][0]["id"]

        delete_dataset_user_response = self.delete_dataset_user(
            client, owner_id, dataset_id
        )
        assert delete_dataset_user_response.status_code == 200

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 0

    def test_get_dataset_by_id_with_invalid_dataset_id(self, client, session):
        dataset = self.get_dataset_by_id(client, self.invalid_dataset_id)
        assert dataset.status_code == 404

    def test_update_dataset_with_invalid_dataset_id(
        self, client, session, default_dataset_payload
    ):
        dataset = self.update_default_dataset(
            client, default_dataset_payload, self.invalid_dataset_id
        )
        assert dataset.status_code == 404

    def test_remove_dataset_with_invalid_dataset_id(self, client, session):
        dataset = self.delete_default_dataset(client, self.invalid_dataset_id)
        assert dataset.status_code == 404

    def test_remove_user_from_dataset_with_invalid_dataset_id(
        self, client, session, default_user
    ):
        dataset = self.delete_dataset_user(
            client, default_user.id, self.invalid_dataset_id
        )
        assert dataset.status_code == 404

    def test_remove_user_from_dataset_with_invalid_user_id(
        self, client, session, default_dataset_payload
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()
        dataset_id = created_dataset.json()["id"]

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 1

        delete_dataset_user_response = self.delete_dataset_user(
            client, self.invalid_dataset_id, dataset_id
        )
        assert delete_dataset_user_response.status_code == 404

    def test_add_already_existing_dataset_owner_to_dataset(
        self, client, session, default_dataset_payload, default_user
    ):
        created_dataset = self.create_default_dataset(client, default_dataset_payload)
        assert created_dataset.status_code == 200
        assert "id" in created_dataset.json()
        dataset_id = created_dataset.json()["id"]

        dataset = self.get_dataset_by_id(client, dataset_id)
        assert dataset.status_code == 200
        assert len(dataset.json()["owners"]) == 1

        owner_id = dataset.json()["owners"][0]["id"]
        added_dataset = self.add_user_to_dataset(client, owner_id, dataset_id)
        assert added_dataset.status_code == 400

    @staticmethod
    def default_dataset_about_payload():
        return {"about": "Updated Dataset Description"}

    @staticmethod
    def create_default_dataset(client, default_dataset_payload):
        response = client.post(ENDPOINT, json=default_dataset_payload)
        return response

    @staticmethod
    def update_default_dataset(client, default_dataset_payload, dataset_id):
        response = client.put(f"{ENDPOINT}/{dataset_id}", json=default_dataset_payload)
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

    @staticmethod
    def add_user_to_dataset(client, user_id, dataset_id):
        response = client.post(f"{ENDPOINT}/{dataset_id}/user/{user_id}")
        return response
