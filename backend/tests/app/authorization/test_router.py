import uuid

import pytest
from fastapi.testclient import TestClient
from tests.factories import UserFactory

from app.authorization.schema import AccessResponse
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization

ENDPOINT = "/api/authz"


class TestAuthorizationRouter:
    def test_check_access(self, client: TestClient, enable_authorizer):
        action = AuthorizationAction.GLOBAL__UPDATE_CONFIGURATION
        response = client.get(f"{ENDPOINT}/access/{action}")
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.allowed is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_check_access_authorized(
        self, client: TestClient, authorizer: Authorization, enable_authorizer
    ):
        user = UserFactory(external_id="sub")
        role_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        action = AuthorizationAction.GLOBAL__DELETE_USER

        await authorizer.sync_role_permissions(
            role_id=str(role_id),
            actions=[action],
        )
        await authorizer.assign_resource_role(
            user_id=str(user.id), role_id=str(role_id), resource_id=str(resource_id)
        )

        response = client.get(f"{ENDPOINT}/access/{action}?resource={resource_id}")
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.allowed is True
