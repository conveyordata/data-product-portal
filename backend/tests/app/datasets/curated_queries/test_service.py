from app.datasets.curated_queries.schema_request import DatasetCuratedQueryInput
from app.datasets.curated_queries.service import DatasetCuratedQueryService
from tests.factories import DatasetFactory


class TestCuratedQueriesService:
    def test_replace_curated_queries_orders_results(self, session):
        dataset = DatasetFactory()
        service = DatasetCuratedQueryService(session)

        curated_queries = [
            DatasetCuratedQueryInput(
                title="Secondary rollup",
                description=None,
                query_text="SELECT 2",
                sort_order=5,
            ),
            DatasetCuratedQueryInput(
                title="Primary spotlight",
                description="Focus on highest priority",
                query_text="SELECT 1",
                sort_order=1,
            ),
            DatasetCuratedQueryInput(
                title="Auto-indexed",
                description=None,
                query_text="SELECT 3",
            ),
        ]

        result = service.replace_curated_queries(dataset.id, curated_queries)
        assert [item.title for item in result.dataset_curated_queries] == [
            "Primary spotlight",
            "Auto-indexed",
            "Secondary rollup",
        ]

    def test_replace_curated_queries_clears_existing(self, session):
        dataset = DatasetFactory()
        service = DatasetCuratedQueryService(session)

        service.replace_curated_queries(
            dataset.id,
            [
                DatasetCuratedQueryInput(
                    title="Keep me",
                    description=None,
                    query_text="SELECT 1",
                )
            ],
        )

        result_after_clear = service.replace_curated_queries(dataset.id, [])
        assert result_after_clear.dataset_curated_queries == []
