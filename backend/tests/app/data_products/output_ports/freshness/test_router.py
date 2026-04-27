from datetime import UTC, datetime, time, timedelta

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    FreshnessObservationFactory,
    FreshnessSloFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


def _assign_update_properties_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[
            AuthorizationAction.OUTPUT_PORT__UPDATE_PROPERTIES,
            AuthorizationAction.OUTPUT_PORT__DELETE,
        ],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, dataset_id=dataset.id
    )
    return user


def _assign_update_freshness_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[
            AuthorizationAction.OUTPUT_PORT__UPDATE_FRESHNESS,
            AuthorizationAction.OUTPUT_PORT__DELETE,
        ],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, dataset_id=dataset.id
    )
    return user


class TestFreshnessSloRouter:
    def test_get_slo_not_found(self, client, session):
        dataset = DatasetFactory()
        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo"
        )
        assert response.status_code == 404

    def test_put_slo_creates(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo",
            json={"deadline_time": "08:00:00"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["deadline_time"] == "08:00:00"
        assert body["status"] == "unknown"

    def test_put_slo_updates_existing(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        FreshnessSloFactory(output_port_id=dataset.id, deadline_time=time(8, 0, 0))

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo",
            json={"deadline_time": "10:00:00"},
        )
        assert response.status_code == 200
        assert response.json()["deadline_time"] == "10:00:00"

    def test_put_slo_no_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()

        response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo",
            json={"deadline_time": "08:00:00"},
        )
        assert response.status_code == 403

    def test_delete_slo(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)
        FreshnessSloFactory(output_port_id=dataset.id)

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo"
        )
        assert response.status_code == 204

    def test_delete_slo_not_found(self, client, session):
        dataset = DatasetFactory()
        _assign_update_properties_role(session, dataset)

        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo"
        )
        assert response.status_code == 404

    def test_post_observation_requires_freshness_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()

        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_observations",
            json={"last_refreshed_at": datetime.now(UTC).isoformat()},
        )
        assert response.status_code == 403

    def test_post_observation_records_and_returns_status(self, client, session):
        dataset = DatasetFactory()
        _assign_update_freshness_role(session, dataset)
        # deadline_time=time(0,0,0): FRESH is returned when last_refreshed >= today_start,
        # independent of the deadline — observation is "now", so always fresh.
        FreshnessSloFactory(output_port_id=dataset.id, deadline_time=time(0, 0, 0))

        payload = {"last_refreshed_at": datetime.now(UTC).isoformat()}
        response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_observations",
            json=payload,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "fresh"
        assert "last_refreshed_at" in body

    def test_get_slo_returns_status_with_latest_observation(self, client, session):
        dataset = DatasetFactory()
        # deadline_time=time(0,0,0): midnight ensures now_utc >= deadline_today is
        # always true (any time of day > midnight), so a stale observation returns STALE.
        FreshnessSloFactory(output_port_id=dataset.id, deadline_time=time(0, 0, 0))
        FreshnessObservationFactory(
            output_port_id=dataset.id,
            last_refreshed_at=datetime.now(UTC) - timedelta(days=2),
        )

        response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/freshness_slo"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "stale"
        assert body["last_refreshed_at"] is not None
