from app.datasets.enums import DatasetAccessType

DATA_PRODUCTS_DATASETS_ENDPOINT = "/api/data_product_dataset_links"
DATA_PRODUCTS_ENDPOINT = "/api/data_products"
DATASETS_ENDPOINT = "/api/datasets"


class TestDataProductsDatasetsRouter:
    def test_request_data_product_link(
        self, client, session, default_data_product_payload, default_dataset_payload
    ):
        data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert data_product.status_code == 200
        data_product_id = data_product.json()["id"]

        dataset = self.create_default_dataset(client, default_dataset_payload)
        assert dataset.status_code == 200
        dataset_id = dataset.json()["id"]

        link = self.request_default_data_product_dataset_link(
            client, data_product_id, dataset_id
        )
        assert link.status_code == 200

    def test_approve_data_product_link(
        self, client, session, default_data_product_payload, default_dataset_payload
    ):
        data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert data_product.status_code == 200
        data_product_id = data_product.json()["id"]

        dataset = self.create_default_dataset(client, default_dataset_payload)
        assert dataset.status_code == 200
        dataset_id = dataset.json()["id"]

        link = self.request_default_data_product_dataset_link(
            client, data_product_id, dataset_id
        )
        assert link.status_code == 200

        link_id = link.json()["id"]
        approved_link = self.approve_default_data_product_dataset_link(client, link_id)
        assert approved_link.status_code == 200

    def test_deny_data_product_link(
        self, client, session, default_data_product_payload, default_dataset_payload
    ):
        data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert data_product.status_code == 200
        data_product_id = data_product.json()["id"]

        dataset = self.create_default_dataset(client, default_dataset_payload)
        assert dataset.status_code == 200
        dataset_id = dataset.json()["id"]

        link = self.request_default_data_product_dataset_link(
            client, data_product_id, dataset_id
        )
        assert link.status_code == 200

        link_id = link.json()["id"]
        denied_link = self.deny_default_data_product_dataset_link(client, link_id)
        assert denied_link.status_code == 200

    def test_remove_data_product_link(
        self, client, session, default_data_product_payload, default_dataset_payload
    ):
        data_product = self.create_default_data_product(
            client, default_data_product_payload
        )
        assert data_product.status_code == 200
        data_product_id = data_product.json()["id"]

        dataset = self.create_default_dataset(client, default_dataset_payload)
        assert dataset.status_code == 200
        dataset_id = dataset.json()["id"]

        link = self.request_default_data_product_dataset_link(
            client, data_product_id, dataset_id
        )
        assert link.status_code == 200

        link_id = link.json()["id"]
        removed_link = self.remove_data_product_dataset_link(client, link_id)
        assert removed_link.status_code == 200

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

    @staticmethod
    def create_default_dataset(client, default_dataset_payload):
        response = client.post(DATASETS_ENDPOINT, json=default_dataset_payload)
        return response

    @staticmethod
    def create_default_data_product(client, default_data_product_payload):
        response = client.post(
            DATA_PRODUCTS_ENDPOINT, json=default_data_product_payload
        )
        return response

    @staticmethod
    def request_default_data_product_dataset_link(client, data_product_id, dataset_id):
        response = client.post(
            f"{DATA_PRODUCTS_ENDPOINT}/{data_product_id}/dataset/{dataset_id}"
        )
        return response

    @staticmethod
    def approve_default_data_product_dataset_link(client, link_id):
        response = client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/approve/{link_id}")
        return response

    @staticmethod
    def deny_default_data_product_dataset_link(client, link_id):
        response = client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/deny/{link_id}")
        return response

    @staticmethod
    def remove_data_product_dataset_link(client, link_id):
        response = client.post(f"{DATA_PRODUCTS_DATASETS_ENDPOINT}/remove/{link_id}")
        return response
