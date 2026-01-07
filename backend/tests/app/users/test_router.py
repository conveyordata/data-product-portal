import pytest

from app.authorization.roles.schema import Scope
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.app.data_products.output_port_technical_assets_link.test_router import (
    DATA_OUTPUTS_ENDPOINT,
)
from tests.factories import UserFactory
from tests.factories.data_output import DataOutputFactory
from tests.factories.data_outputs_datasets import DataOutputDatasetAssociationFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.dataset import DatasetFactory
from tests.factories.role import RoleFactory
from tests.factories.role_assignment_data_product import (
    DataProductRoleAssignmentFactory,
)
from tests.factories.role_assignment_dataset import DatasetRoleAssignmentFactory
from tests.factories.role_assignment_global import GlobalRoleAssignmentFactory

ENDPOINT = "/api/users"


class TestUsersRouter:
    def test_get_users(self, client):
        UserFactory()

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_get_users_v2(self, client):
        UserFactory()

        response = client.get("/api/v2/users")
        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 1

    def test_remove_user_not_admin(self, client):
        user = UserFactory()

        response = client.delete(f"{ENDPOINT}/{user.id}")
        assert response.status_code == 403

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.usefixtures("admin")
    def test_remove_user(self, client):
        user = UserFactory()

        response = client.get(f"{ENDPOINT}")
        response = client.delete(f"{ENDPOINT}/{user.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_post_user_not_admin(self, client):
        response = client.post(f"{ENDPOINT}")
        assert response.status_code == 403

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_post_user(self, client):
        response = client.post(
            f"{ENDPOINT}",
            json={
                "email": "test@user.com",
                "external_id": "test-user",
                "first_name": "test",
                "last_name": "user",
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_post_has_seen_tour(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()) == 1
        assert response.json()[0]["has_seen_tour"] is False
        response = client.post(f"{ENDPOINT}/seen_tour")
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()) == 1
        assert response.json()[0]["has_seen_tour"] is True
        assert response.status_code == 200

    def test_post_has_seen_tour_v2(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()) == 1
        assert response.json()[0]["has_seen_tour"] is False
        response = client.post("/api/v2/users/current/seen_tour")
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()) == 1
        assert response.json()[0]["has_seen_tour"] is True
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_post_user_default_admin(self, client):
        response = client.post(
            f"{ENDPOINT}",
            json={
                "email": "test@user.com",
                "external_id": "test-user",
                "first_name": "test",
                "last_name": "user",
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_can_become_admin_not_admin(self, client):
        user = UserFactory(
            external_id=settings.DEFAULT_USERNAME, can_become_admin=False
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": True,
            },
        )
        assert response.status_code == 403

    def test_can_unbecome_admin(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=True)
        UserFactory(can_become_admin=True)
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": False,
            },
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT}")
        data = response.json()
        for user_data in data:
            if user_data["id"] == str(user.id):
                assert user_data["can_become_admin"] is False

    def test_can_not_unbecome_admin_latest_admin(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=True)
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": False,
            },
        )
        assert response.status_code == 400
        response = client.get(f"{ENDPOINT}")
        data = response.json()
        for user_data in data:
            if user_data["id"] == str(user.id):
                assert user_data["can_become_admin"] is True

    def test_can_become_admin(self, client):
        user = UserFactory(
            external_id=settings.DEFAULT_USERNAME, can_become_admin=False
        )
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": True,
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        data = response.json()
        for user_data in data:
            if user_data["id"] == str(user.id):
                assert user_data["can_become_admin"] is True

    def test_get_pending_actions_no_action(self, client):
        ds = DatasetFactory()
        DataOutputDatasetAssociationFactory(dataset=ds)
        response = client.get("/api/v2/users/current/pending_actions")
        assert response.json() == {"pending_actions": []}

    def test_get_pending_actions(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        data_output = DataOutputFactory(owner=data_product)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        ds = DatasetFactory(data_product=data_product)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[AuthorizationAction.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(user_id=user.id, role_id=role.id, dataset_id=ds.id)

        response = client.post(
            f"{DATA_OUTPUTS_ENDPOINT}/{data_output.id}/dataset/{ds.id}"
        )
        assert response.status_code == 200
        response = client.get("/api/v2/users/current/pending_actions")
        assert response.json()["pending_actions"][0]["technical_asset_id"] == str(
            data_output.id
        )
        assert response.json()["pending_actions"][0]["status"] == "pending"
