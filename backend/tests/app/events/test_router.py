from app.core.authz import Action
from app.roles.schema import Scope
from app.settings import settings
from tests.factories import DataOutputFactory, DataProductFactory, DatasetFactory
from tests.factories.role import RoleFactory
from tests.factories.role_assignment_data_product import (
    DataProductRoleAssignmentFactory,
)
from tests.factories.user import UserFactory

ENDPOINT = "/api/events"


class TestEventsRouter:
    def test_latest_event_timestamp_is_none(self, client):
        data_product = DataProductFactory()
        DatasetFactory()
        DataOutputFactory(owner=data_product)
        response = client.get(f"{ENDPOINT}/latest")
        assert response.json() is None

    def test_latest_event_timestamp(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_PROPERTIES],
        )
        DataProductRoleAssignmentFactory(
            user_id=user.id,
            role_id=role.id,
            data_product_id=data_product.id,
        )
        response = client.put(
            f"{'/api/data_products'}/{data_product.id}/about", json={"about": "active"}
        )
        response = client.get(f"{ENDPOINT}/latest")
        assert response.json() is not None
