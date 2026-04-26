from datetime import date, timedelta

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    OutputPortCostRecordFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


def _assign_update_cost_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[
            AuthorizationAction.OUTPUT_PORT__UPDATE_COST,
            AuthorizationAction.OUTPUT_PORT__DELETE,
        ],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, dataset_id=dataset.id
    )
    return user


class TestOutputPortCostRouter:
    def test_post_cost_record(self, client, session):
        dataset = DatasetFactory()
        _assign_update_cost_role(session, dataset)

        payload = {
            "recorded_at": "2026-04-01",
            "compute_cost": "45.00",
            "storage_cost": "30.00",
            "platform_overhead_cost": "15.00",
        }

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/cost",
            json=payload,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["recorded_at"] == "2026-04-01"
        assert body["output_port_id"] == str(dataset.id)
        assert "total_cost" in body

    def test_post_cost_record_defaults_recorded_at_to_today(self, client, session):
        dataset = DatasetFactory()
        _assign_update_cost_role(session, dataset)

        payload = {
            "compute_cost": "10.00",
            "storage_cost": "5.00",
            "platform_overhead_cost": "2.00",
        }

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/cost",
            json=payload,
        )
        assert response.status_code == 201
        body = response.json()
        assert body["recorded_at"] == date.today().isoformat()

    def test_post_cost_record_no_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()

        payload = {
            "recorded_at": "2026-04-01",
            "compute_cost": "45.00",
            "storage_cost": "30.00",
            "platform_overhead_cost": "15.00",
        }

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/cost",
            json=payload,
        )
        assert response.status_code == 403

    def test_get_cost_history(self, client, session):
        dataset = DatasetFactory()

        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=5),
            compute_cost="40.00",
            storage_cost="20.00",
            platform_overhead_cost="10.00",
        )
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=2),
            compute_cost="50.00",
            storage_cost="25.00",
            platform_overhead_cost="12.00",
        )

        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/cost",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["output_port_id"] == str(dataset.id)
        assert len(body["records"]) == 2
        # ordered most recent first
        assert body["records"][0]["recorded_at"] > body["records"][1]["recorded_at"]

    def test_get_cost_history_respects_day_range(self, client, session):
        dataset = DatasetFactory()

        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=5),
        )
        OutputPortCostRecordFactory(
            output_port_id=dataset.id,
            recorded_at=date.today() - timedelta(days=100),
        )

        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/cost"
            "?day_range=30",
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["records"]) == 1

    def test_get_cost_history_empty(self, client, session):
        dataset = DatasetFactory()

        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/cost",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["records"] == []
