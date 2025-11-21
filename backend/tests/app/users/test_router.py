import pytest
from tests.factories import UserFactory
from tests.factories.role import RoleFactory
from tests.factories.role_assignment_global import GlobalRoleAssignmentFactory

from app.core.authz.actions import AuthorizationAction
from app.roles.schema import Scope
from app.settings import settings

ENDPOINT = "/api/users"


class TestUsersRouter:
    def test_get_users(self, client):
        UserFactory()

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

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
        response = client.post(
            f"{ENDPOINT}/can_become_admin",
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
        response = client.post(
            f"{ENDPOINT}/can_become_admin",
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
        response = client.post(
            f"{ENDPOINT}/can_become_admin",
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
        response = client.post(
            f"{ENDPOINT}/can_become_admin",
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
