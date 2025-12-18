from datetime import date
from typing import Optional
from uuid import UUID
from warnings import deprecated

from app.shared.schema import ORMModel


class OutputPortQueryStatsResponse(ORMModel):
    date: date
    consumer_data_product_id: UUID
    query_count: int
    consumer_data_product_name: Optional[str] = None


@deprecated("Use OutputPortQueryStatsResponses instead")
class DatasetQueryStatsResponses(ORMModel):
    dataset_query_stats_daily_responses: list[OutputPortQueryStatsResponse]


class OutputPortQueryStatsResponses(ORMModel):
    output_port_query_stats_responses: list[OutputPortQueryStatsResponse]
