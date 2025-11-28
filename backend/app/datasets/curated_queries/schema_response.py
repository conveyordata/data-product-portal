from datetime import datetime
from uuid import UUID

from app.shared.schema import ORMModel


class DatasetCuratedQuery(ORMModel):
    curated_query_id: UUID
    output_port_id: UUID
    title: str
    description: str | None
    query_text: str
    sort_order: int
    created_at: datetime
    updated_at: datetime | None


class DatasetCuratedQueries(ORMModel):
    dataset_curated_queries: list[DatasetCuratedQuery]
