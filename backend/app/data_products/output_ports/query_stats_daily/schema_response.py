from datetime import date
from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class DatasetQueryStatsDailyResponse(ORMModel):
    date: date
    consumer_data_product_id: UUID
    query_count: int
    consumer_data_product_name: Optional[str] = None


class DatasetQueryStatsDailyResponses(ORMModel):
    dataset_query_stats_daily_responses: list[DatasetQueryStatsDailyResponse]
