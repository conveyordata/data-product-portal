from app.authorization.roles.schema import Scope
from app.authorization.roles.service import RoleService
from app.core.authz.actions import AuthorizationAction
from app.data_products.output_ports.curated_queries.schema_request import (
    OutputPortCuratedQueryInput,
)
from app.data_products.output_ports.curated_queries.service import (
    DatasetCuratedQueryService,
)
from app.settings import settings
from tests.factories import (
    DatasetFactory,
    DatasetRoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)

ENDPOINT = "/api/datasets"


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


class TestCuratedQueriesRouter:
    def test_curated_queries_put(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        payload = {
            "curated_queries": [
                {
                    "title": "Top enrolling sites",
                    "description": "Ranks sites by screened patients.",
                    "query_text": "SELECT site_id, screened_patients FROM enrollment ORDER BY screened_patients DESC LIMIT 5;",
                },
                {
                    "title": "New deviations",
                    "description": "Shows protocol deviations raised this week.",
                    "query_text": "SELECT * FROM protocol_deviations WHERE deviation_date >= CURRENT_DATE - INTERVAL '7 days';",
                },
            ]
        }

        put_response = client.put(
            f"{ENDPOINT}/{dataset.id}/usage/curated_queries", json=payload
        )
        assert put_response.status_code == 200
        body = put_response.json()
        assert len(body["dataset_curated_queries"]) == 2
        assert body["dataset_curated_queries"][0]["title"] == "Top enrolling sites"
        assert body["dataset_curated_queries"][1]["title"] == "New deviations"

    def test_curated_queries_get(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        service = DatasetCuratedQueryService(session)
        service.replace_curated_queries(
            dataset.id,
            [
                OutputPortCuratedQueryInput(
                    title="Existing query",
                    description="Stored during setup",
                    query_text="SELECT 1",
                )
            ],
        )

        get_response = client.get(f"{ENDPOINT}/{dataset.id}/usage/curated_queries")
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data["dataset_curated_queries"]) == 1
        assert data["dataset_curated_queries"][0]["title"] == "Existing query"
