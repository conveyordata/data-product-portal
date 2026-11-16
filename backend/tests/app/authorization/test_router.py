import uuid

from fastapi.testclient import TestClient

from app.authorization.schema_response import AccessResponse
from app.core.authz import Action, CasbinPolicies
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/authz"


class TestAuthorizationRouter:
    def test_check_access(self, client: TestClient):
        action = Action.GLOBAL__UPDATE_CONFIGURATION
        response = client.get(f"{ENDPOINT}/access/{action}")
        assert response.status_code == 200

        access = AccessResponse(**response.json())
        assert access.allowed is False

    def test_check_access_authorized(
        self, client: TestClient, authorizer: CasbinPolicies
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
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

    def test_check_access_authorized_by_data_product_role(
        self, client: TestClient, authorizer: CasbinPolicies
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        output_port = OutputPortFactory(data_product=data_product)
        action = Action.OUTPUT_PORT__UPDATE_PROPERTIES
        role = RoleFactory(permissions=[action])
        DataProductRoleAssignmentFactory(
            role_id=role.id, identity_id=user.id, data_product_id=data_product.id
        )

        response = client.get(f"{ENDPOINT}/access/{action}?resource={output_port.id}")

        assert response.status_code == 200
        assert AccessResponse(**response.json()).allowed is True

    def test_check_access__consumer_member_reads_invite_only_output_port(
        self, client: TestClient
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        consumer = DataProductFactory()
        DataProductRoleAssignmentFactory(
            identity_id=user.id,
            data_product_id=consumer.id,
            role_id=RoleFactory.data_product_owner().id,
        )
        output_port = OutputPortFactory(
            access_function=OutputPortAccessFunction.PRIVATE
        )
        InputPortFactory(
            consuming_abstract_data_product=consumer, output_port=output_port
        )
        action = Action.HIDDEN__OUTPUT_PORT__READ

        response = client.get(f"{ENDPOINT}/access/{action}?resource={output_port.id}")

        assert response.status_code == 200
        assert AccessResponse(**response.json()).allowed is True

    def test_check_access__owner_member_reads_invite_only_output_port(
        self, client: TestClient
    ):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        DataProductRoleAssignmentFactory(
            identity_id=user.id,
            data_product_id=data_product.id,
            role_id=RoleFactory.data_product_owner().id,
        )
        output_port = OutputPortFactory(
            data_product=data_product, access_function=OutputPortAccessFunction.PRIVATE
        )
        action = Action.HIDDEN__OUTPUT_PORT__READ

        response = client.get(f"{ENDPOINT}/access/{action}?resource={output_port.id}")

        assert response.status_code == 200
        assert AccessResponse(**response.json()).allowed is True

    def test_is_admin(self, client: TestClient):
        response = client.get(f"{ENDPOINT}/admin")
        assert response.status_code == 200
        assert response.json()["is_admin"] is False

    def test_is_admin_authorized(self, client: TestClient, admin):
        response = client.get(f"{ENDPOINT}/admin")
        assert response.status_code == 200
        assert response.json()["is_admin"] is True
