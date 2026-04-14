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

ENDPOINT = "/api/v2/data_products"


def _assign_update_role(session, dataset):
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


class TestCuratedQueriesRouter:
    @staticmethod
    def curate_queries_payload():
        return {
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

    def test_curated_queries_put(self, client, session):
        dataset = DatasetFactory()
        _assign_update_role(session, dataset)

        put_response = client.put(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/curated_queries",
            json=self.curate_queries_payload(),
        )
        assert put_response.status_code == 200
        body = put_response.json()
        assert len(body["output_port_curated_queries"]) == 2
        assert body["output_port_curated_queries"][0]["title"] == "Top enrolling sites"
        assert body["output_port_curated_queries"][1]["title"] == "New deviations"

    def test_delete_output_port_curated_query(self, client, session):
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
        response = client.delete(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}"
        )

        assert response.status_code == 200

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

        get_response = client.get(
            f"{ENDPOINT}/{dataset.data_product.id}/output_ports/{dataset.id}/curated_queries"
        )
        assert get_response.status_code == 200
        data = get_response.json()
        assert len(data["output_port_curated_queries"]) == 1
        assert data["output_port_curated_queries"][0]["title"] == "Existing query"
