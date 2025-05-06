import uuid

import pytest
from fastapi.testclient import TestClient
from tests.factories import UserFactory
from tests.factories.data_product import DataProductFactory
from tests.factories.data_product_membership import DataProductMembershipFactory
from tests.factories.dataset import DatasetFactory
from tests.factories.role import RoleFactory
from tests.factories.role_assignment_data_product import (
    DataProductRoleAssignmentFactory,
)
from tests.factories.role_assignment_dataset import DatasetRoleAssignmentFactory

from app.authorization.schema import AccessResponse
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.data_products.model import DataProduct
from app.datasets.schema import Dataset
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Role, Scope

ENDPOINT = "/api/authz"
ENDPOINT_ROLE_ASSIGNMENT_DATASET = "/api/role_assignments/dataset"
ENDPOINT_ROLE_ASSIGNMENT_DATA_PRODUCT = "/api/role_assignments/data_product"
ENDPOINT_DATASET = "/api/datasets"
ENDPOINT_DATA_PRODUCT = "/api/data_products"


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

    @pytest.mark.asyncio(loop_scope="session")
    async def test_delete_dataset_with_role_assignment(
        self, client: TestClient, authorizer: Authorization, enable_authorizer
    ):
        user = UserFactory(external_id="sub")
        role_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        dataset: Dataset = DatasetFactory(owners=[user], id=resource_id)
        action = AuthorizationAction.DATASET__DELETE
        role: Role = RoleFactory(scope=Scope.DATASET, id=role_id)

        DatasetRoleAssignmentFactory(
            dataset_id=dataset.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
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

        response = client.get(f"{ENDPOINT_ROLE_ASSIGNMENT_DATASET}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = self.delete_default_dataset(client, dataset.id)
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT_ROLE_ASSIGNMENT_DATASET}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        response = client.get(f"{ENDPOINT}/access/{action}?resource={resource_id}")
        access = AccessResponse(**response.json())
        assert access.allowed is False

    @pytest.mark.asyncio(loop_scope="session")
    async def test_delete_data_product_with_role_assignment(
        self, client: TestClient, authorizer: Authorization, enable_authorizer
    ):
        user = UserFactory(external_id="sub")
        role_id = uuid.uuid4()
        resource_id = uuid.uuid4()
        data_product: DataProduct = DataProductMembershipFactory(
            user=user, data_product=DataProductFactory(id=resource_id)
        ).data_product
        action = AuthorizationAction.DATA_PRODUCT__DELETE
        role: Role = RoleFactory(scope=Scope.DATA_PRODUCT, id=role_id)

        DataProductRoleAssignmentFactory(
            data_product_id=data_product.id,
            user_id=user.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )
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

        response = client.get(f"{ENDPOINT_ROLE_ASSIGNMENT_DATA_PRODUCT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        response = self.delete_data_product(client, data_product.id)
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT_ROLE_ASSIGNMENT_DATA_PRODUCT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        response = client.get(f"{ENDPOINT}/access/{action}?resource={resource_id}")
        access = AccessResponse(**response.json())
        assert access.allowed is False

    @staticmethod
    def delete_default_dataset(client, dataset_id):
        return client.delete(f"{ENDPOINT_DATASET}/{dataset_id}")

    @staticmethod
    def delete_data_product(client, data_product_id):
        return client.delete(f"{ENDPOINT_DATA_PRODUCT}/{data_product_id}")
