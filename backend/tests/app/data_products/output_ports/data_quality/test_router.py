from datetime import UTC, datetime, timedelta

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.data_quality.schema_request import (
    OutputPortDataQualitySummary,
)
from app.data_products.output_ports.data_quality.service import (
    DatasetDataQualityService,
)
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/data_products"


def _assign_update_role(session, dataset):
    RoleService(db=session).initialize_prototype_roles()
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.DATASET,
        permissions=[AuthorizationAction.DATASET__UPDATE_PROPERTIES],
    )
    DatasetRoleAssignmentFactory(
        user_id=user.id, role_id=role.id, dataset_id=dataset.id
    )
    return user


class TestDataQualityRouter:
    def test_post_data_quality(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        payload = {
            "overall_status": "pass",
            "details_url": "https://mycustomdomain.be/run1",
            "created_at": datetime.now().isoformat(),
            "technical_assets": [
                {"name": "table1", "status": "pass"},
                {"name": "table2", "status": "fail"},
            ],
        }

        post_response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary",
            json=payload,
        )
        assert post_response.status_code == 200
        body = post_response.json()
        assert len(body["technical_assets"]) == 2
        assert body["overall_status"] == payload["overall_status"]
        assert body["details_url"] == payload["details_url"]

    def test_post_data_quality_with_dimensions(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        payload = {
            "overall_status": "pass",
            "created_at": datetime.now().isoformat(),
            "technical_assets": [
                {"name": "table1", "status": "pass"},
            ],
            "dimensions": {"completeness": "pass", "validity": "fail"},
        }

        post_response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary",
            json=payload,
        )
        assert post_response.status_code == 200
        body = post_response.json()
        assert len(body["dimensions"]) == 2
        assert body["dimensions"]["validity"] == "fail"
        assert body["dimensions"]["completeness"] == "pass"

    def test_get_latest_data_quality_result_no_results(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        get_response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary"
        )
        assert get_response.status_code == 404
        data = get_response.json()
        assert "No data quality summary found for output port" in data["detail"]

    def test_get_latest_data_quality_result(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        service = DatasetDataQualityService(session)
        service.save_data_quality_summary(
            dataset.id,
            OutputPortDataQualitySummary(
                created_at=datetime.now(UTC) - timedelta(days=1),
                overall_status=DataQualityStatus.FAIL,
                technical_assets=[],
                dimensions={},
            ),
        )

        summary_last = service.save_data_quality_summary(
            dataset.id,
            OutputPortDataQualitySummary(
                created_at=datetime.now(UTC),
                overall_status=DataQualityStatus.PASS,
                technical_assets=[],
                dimensions={},
            ),
        )

        get_response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary"
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["overall_status"] == DataQualityStatus.PASS
        assert data["created_at"] == summary_last.created_at.isoformat().replace(
            "+00:00", "Z"
        )
