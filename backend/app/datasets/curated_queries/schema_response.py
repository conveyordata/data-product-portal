from datetime import datetime
from uuid import UUID

from app.shared.schema import ORMModel


class DatasetCuratedQuery(ORMModel):
    output_port_id: UUID
    sort_order: int
    title: str
    description: str | None
    query_text: str
    created_at: datetime
    updated_at: datetime | None


class DatasetCuratedQueries(ORMModel):
    dataset_curated_queries: list[DatasetCuratedQuery]
