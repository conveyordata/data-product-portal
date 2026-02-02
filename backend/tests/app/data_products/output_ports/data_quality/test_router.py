from datetime import UTC, datetime, timedelta

from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.data_quality.schema_request import (
    DataQualityTechnicalAsset,
    OutputPortDataQualitySummary,
)
from app.data_products.output_ports.data_quality.service import (
    OutputPortDataQualityService,
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
        permissions=[AuthorizationAction.OUTPUT_PORT__UPDATE_DATA_QUALITY],
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
            "overall_status": "success",
            "details_url": "https://mycustomdomain.be/run1",
            "created_at": datetime.now().isoformat(),
            "technical_assets": [
                {"name": "table1", "status": "success"},
                {"name": "table2", "status": "failure"},
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

    def test_post_data_quality_no_permissions(self, client, session):
        dataset = DatasetFactory()
        RoleService(db=session).initialize_prototype_roles()

        payload = {
            "overall_status": "success",
            "details_url": "https://mycustomdomain.be/run1",
            "created_at": datetime.now().isoformat(),
            "technical_assets": [
                {"name": "table1", "status": "success"},
                {"name": "table2", "status": "failure"},
            ],
        }

        post_response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary",
            json=payload,
        )
        assert post_response.status_code == 403

    def test_post_data_quality_with_dimensions(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        payload = {
            "overall_status": "success",
            "created_at": datetime.now().isoformat(),
            "technical_assets": [
                {"name": "table1", "status": "success"},
            ],
            "dimensions": {"completeness": "success", "validity": "failure"},
        }

        post_response = client.post(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary",
            json=payload,
        )
        assert post_response.status_code == 200
        body = post_response.json()
        assert len(body["dimensions"]) == 2
        assert body["dimensions"]["validity"] == "failure"
        assert body["dimensions"]["completeness"] == "success"

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

        service = OutputPortDataQualityService(session)
        service.save_data_quality_summary(
            dataset.id,
            OutputPortDataQualitySummary(
                created_at=datetime.now(UTC) - timedelta(days=1),
                overall_status=DataQualityStatus.FAILURE,
                technical_assets=[],
            ),
        )

        summary_last = service.save_data_quality_summary(
            dataset.id,
            OutputPortDataQualitySummary(
                created_at=datetime.now(UTC),
                overall_status=DataQualityStatus.SUCCESS,
                technical_assets=[],
                dimensions={
                    "validity": DataQualityStatus.FAILURE,
                    "completeness": DataQualityStatus.SUCCESS,
                },
            ),
        )

        get_response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary"
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["overall_status"] == DataQualityStatus.SUCCESS
        assert data["created_at"] == summary_last.created_at.isoformat().replace(
            "+00:00", "Z"
        )
        assert data["dimensions"]["validity"] == DataQualityStatus.FAILURE
        assert data["dimensions"]["completeness"] == DataQualityStatus.SUCCESS

    def test_update_data_quality_summary(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        service = OutputPortDataQualityService(session)
        saved_result = service.save_data_quality_summary(
            dataset.id,
            OutputPortDataQualitySummary(
                created_at=datetime.now(UTC) - timedelta(days=1),
                overall_status=DataQualityStatus.FAILURE,
                technical_assets=[
                    DataQualityTechnicalAsset(
                        name="table1", status=DataQualityStatus.SUCCESS
                    )
                ],
            ),
        )

        updated_ts = datetime.now(UTC).isoformat()
        update_payload = {
            "overall_status": "success",
            "created_at": updated_ts,
            "technical_assets": [
                {"name": "table1", "status": "success"},
            ],
        }

        put_response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/data_quality_summary/{saved_result.id}",
            json=update_payload,
        )
        assert put_response.status_code == 200
        body = put_response.json()
        assert body["overall_status"] == update_payload["overall_status"]
        assert body["created_at"] == updated_ts.replace("+00:00", "Z")
