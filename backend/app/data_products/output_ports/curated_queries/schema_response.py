from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from app.shared.schema import ORMModel


class OutputPortCuratedQuery(ORMModel):
    output_port_id: UUID
    sort_order: int
    title: str
    description: Optional[str]
    query_text: str
    created_at: datetime
    updated_at: Optional[datetime]


class OutputPortCuratedQueries(ORMModel):
    output_port_curated_queries: Sequence[OutputPortCuratedQuery]


@deprecated("Use OutputPortCuratedQueries instead")
class DatasetCuratedQueries(ORMModel):
    dataset_curated_queries: Sequence[OutputPortCuratedQuery]
