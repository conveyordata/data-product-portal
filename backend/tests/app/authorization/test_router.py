import uuid

import pytest
from fastapi.testclient import TestClient
from tests.factories import UserFactory

from app.authorization.schema import AccessRequest, AccessResponse
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization

ENDPOINT = "/api/authz"


class TestAuthorizationRouter:

    def test_check_access(self, client: TestClient):
        request = AccessRequest(
            object_id=None,
            domain=None,
            action=AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS,
        )
        response = client.post(
            f"{ENDPOINT}/access/check", json=request.model_dump(mode="json")
        )
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.access is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_check_access_authorized(
        self, client: TestClient, authorizer: Authorization
    ):
        user = UserFactory(external_id="sub")
        role_id = uuid.uuid4()
        resource_id = uuid.uuid4()

        await authorizer.sync_role_permissions(
            role_id=str(role_id),
            actions=[AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS],
        )
        await authorizer.assign_resource_role(
            user_id=str(user.id), role_id=str(role_id), resource_id=str(resource_id)
        )

        request = AccessRequest(
            object_id=resource_id,
            domain=None,
            action=AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS,
        )
        response = client.post(
            f"{ENDPOINT}/access/check", json=request.model_dump(mode="json")
        )
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.access is True
