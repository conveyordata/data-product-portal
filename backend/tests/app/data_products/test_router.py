import json
from copy import deepcopy

import pytest
from tests.factories import (
    DataProductFactory,
    DataProductTypeFactory,
    DomainFactory,
    TagFactory,
    UserFactory,
)
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.data_product_setting import DataProductSettingFactory
from tests.factories.env_platform_config import EnvPlatformConfigFactory
from tests.factories.environment import EnvironmentFactory
from tests.factories.lifecycle import LifecycleFactory
from tests.factories.platform import PlatformFactory

from app.data_product_memberships.enums import DataProductUserRole
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
        "external_id": "Updated Data Product External ID",
        "tag_ids": [str(tag.id)],
        "type_id": str(data_product_type.id),
        "memberships": [
            {
                "user_id": str(user.id),
                "role": DataProductUserRole.OWNER.value,
            }
        ],
        "lifecycle_id": str(lifecycle.id),
        "domain_id": str(domain.id),
    }


class TestDataProductsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_data_product(self, payload, client, session):
        RoleService(db=session).initialize_prototype_roles()
        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 200
        assert "id" in created_data_product.json()

    def test_create_data_product_no_owner_role(self, payload, client):
        created_data_product = self.create_data_product(client, payload)
        assert created_data_product.status_code == 400

    def test_create_data_product_no_members(self, payload, client):
        create_payload = deepcopy(payload)
        create_payload["memberships"] = []
        created_data_product = self.create_data_product(client, create_payload)
        assert created_data_product.status_code == 422

    def test_create_data_product_no_owner(self, payload, client):
        user = UserFactory()
        memberships = [
            {
                "user_id": str(user.id),
                "role": DataProductUserRole.MEMBER.value,
            }
        ]
        create_payload = deepcopy(payload)
        create_payload["memberships"] = memberships

        created_data_product = self.create_data_product(client, create_payload)
        assert created_data_product.status_code == 422

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
        data_product = DataProductMembershipFactory(user=user).data_product

        response = self.get_conveyor_ide_url(client, data_product.id)
        assert response.status_code == 501

    def test_get_data_product_by_user_id(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(user=user).data_product

        response = self.get_data_product_by_user_id(client, user.id)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(data_product.id)

    def test_get_data_outputs(self, client):
        user = UserFactory(external_id="sub")
        data_product = DataProductMembershipFactory(user=user).data_product
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
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        update_payload = deepcopy(payload)
        update_payload["name"] = "Updated Data Product"
        response = self.update_data_product(client, update_payload, data_product.id)

        assert response.status_code == 200
        assert response.json()["id"] == str(data_product.id)

    def test_update_data_product_about_no_member(self, client):
        data_product = DataProductFactory()
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 403

    def test_update_data_product_about_remove_all_members(self, payload, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        update_payload = deepcopy(payload)
        update_payload["memberships"] = []
        response = self.update_data_product(client, update_payload, data_product.id)
        assert response.status_code == 422

    def test_update_data_product_about_remove_last_owner(self, payload, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        update_payload = deepcopy(payload)
        user = UserFactory()
        memberships = [
            {
                "user_id": str(user.id),
                "role": DataProductUserRole.MEMBER.value,
            }
        ]
        update_payload["memberships"] = memberships
        response = self.update_data_product(client, update_payload, data_product.id)
        assert response.status_code == 422

    def test_update_data_product_about(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = self.update_data_product_about(client, data_product.id)
        assert response.status_code == 200

    def test_remove_data_product_no_member(self, client):
        data_product = DataProductFactory()
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 403

    def test_remove_data_product(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

    def test_update_status_not_owner(self, client):
        data_product = DataProductFactory()
        response = self.update_data_product_status(
            client, {"status": "active"}, data_product.id
        )
        assert response.status_code == 403

    def test_update_status(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = self.get_data_product_by_id(client, data_product.id)
        assert response.json()["status"] == "pending"
        response = self.update_data_product_status(
            client, {"status": "active"}, data_product.id
        )
        response = self.get_data_product_by_id(client, data_product.id)
        assert response.json()["status"] == "active"

    def test_get_data_product_by_id_with_invalid_id(self, client):
        data_product = self.get_data_product_by_id(client, self.invalid_id)
        assert data_product.status_code == 404

    def test_update_data_product_with_invalid_data_product_id(self, client, payload):
        data_product = self.update_data_product(client, payload, self.invalid_id)
        assert data_product.status_code == 404

    def test_remove_data_product_with_invalid_data_product_id(self, client):
        data_product = self.delete_data_product(client, self.invalid_id)
        assert data_product.status_code == 404

    def test_data_product_set_custom_setting_wrong_scope(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        setting = DataProductSettingFactory(scope="dataset")
        response = client.post(
            f"{ENDPOINT}/{data_product.id}/settings/{setting.id}?value=false"
        )
        assert response.status_code == 404

    def test_dataset_set_custom_setting_not_owner(self, client):
        data_product = DataProductFactory()
        setting = DataProductSettingFactory()
        response = client.post(f"{ENDPOINT}/{data_product.id}/settings/{setting.id}")
        assert response.status_code == 403

    def test_dataset_set_custom_setting(self, client):
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
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
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/role?environment=production"
        )
        assert response.status_code == 200
        assert response.json() == env.context.replace("{{}}", data_product.external_id)

    def test_get_signin_url_not_implemented(self, client):
        EnvironmentFactory(name="production")
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/signin_url?environment=production"
        )
        assert (
            response.status_code == 501 or response.status_code == 400
        )  # TODO Add actual AWS test through mocking

    def test_get_databricks_url(self, client):
        env = EnvironmentFactory(name="production")
        platform = PlatformFactory(name="Databricks")
        data_product = DataProductMembershipFactory(
            user=UserFactory(external_id="sub")
        ).data_product
        EnvPlatformConfigFactory(
            environment=env,
            platform=platform,
            config=json.dumps(
                {"workspace_urls": {str(data_product.domain.id): "test_1.com"}}
            ),
        )
        response = client.get(
            f"{ENDPOINT}/{data_product.id}/databricks_workspace_url?"
            "environment=production"
        )
        assert response.status_code == 200
        assert response.json() == "test_1.com"

    @staticmethod
    def create_data_product(client, default_data_product_payload):
        return client.post(ENDPOINT, json=default_data_product_payload)

    @staticmethod
    def update_data_product(client, payload, data_product_id):
        return client.put(f"{ENDPOINT}/{data_product_id}", json=payload)

    @staticmethod
    def update_data_product_about(client, data_product_id):
        data = {"about": "Updated Data Product Description"}
        return client.put(f"{ENDPOINT}/{data_product_id}/about", json=data)

    @staticmethod
    def update_data_product_status(client, status, data_product_id):
        return client.put(f"{ENDPOINT}/{data_product_id}/status", json=status)

    @staticmethod
    def delete_data_product(client, data_product_id):
        return client.delete(f"{ENDPOINT}/{data_product_id}")

    @staticmethod
    def get_data_product_by_id(client, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}")

    @staticmethod
    def get_data_outputs(client, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}/data_outputs")

    @staticmethod
    def get_data_product_by_user_id(client, user_id):
        return client.get(f"{ENDPOINT}/user/{user_id}")

    @staticmethod
    def get_conveyor_ide_url(client, data_product_id):
        return client.get(f"{ENDPOINT}/{data_product_id}/conveyor_ide_url")
