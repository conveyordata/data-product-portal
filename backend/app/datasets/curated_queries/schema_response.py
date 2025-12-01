from datetime import datetime
from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class DatasetCuratedQuery(ORMModel):
    output_port_id: UUID
    sort_order: int
    title: str
    description: Optional[str]
    query_text: str
    created_at: datetime
    updated_at: Optional[datetime]


class DatasetCuratedQueries(ORMModel):
    dataset_curated_queries: list[DatasetCuratedQuery]
