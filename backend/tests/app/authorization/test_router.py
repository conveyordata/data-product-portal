import uuid

from fastapi.testclient import TestClient
from tests.factories import UserFactory

from app.authorization.schema import AccessResponse
from app.core.authz import Action, Authorization

ENDPOINT = "/api/authz"


class TestAuthorizationRouter:
    def test_check_access(self, client: TestClient):
        action = Action.GLOBAL__UPDATE_CONFIGURATION
        response = client.get(f"{ENDPOINT}/access/{action}")
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.allowed is False

    def test_check_access_authorized(
        self, client: TestClient, authorizer: Authorization
    ):
        user = UserFactory(external_id="sub")
        role_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        action = Action.GLOBAL__DELETE_USER

        authorizer.sync_role_permissions(
            role_id=str(role_id),
            actions=[action],
        )
        authorizer.assign_resource_role(
            user_id=str(user.id), role_id=str(role_id), resource_id=str(resource_id)
        )

        response = client.get(f"{ENDPOINT}/access/{action}?resource={resource_id}")
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.allowed is True

    def test_is_admin(self, client: TestClient):
        response = client.get(f"{ENDPOINT}/admin")
        assert response.status_code == 200
        assert response.json() is False

    def test_is_admin_authorized(self, client: TestClient, admin):
        response = client.get(f"{ENDPOINT}/admin")
        assert response.status_code == 200
        assert response.json() is True
