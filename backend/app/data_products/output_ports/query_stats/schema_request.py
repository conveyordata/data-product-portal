from uuid import UUID

from app.shared.schema import ORMModel


class OutputPortQueryStatsUpdate(ORMModel):
    date: str
    consumer_data_product_id: UUID
    query_count: int


class DatasetQueryStatsUpdates(ORMModel):
    dataset_query_stats_daily_updates: list[OutputPortQueryStatsUpdate]


class UpdateOutputPortQueryStatus(ORMModel):
    output_port_query_stats_updates: list[OutputPortQueryStatsUpdate]


class OutputPortQueryStatsDelete(ORMModel):
    date: str
    consumer_data_product_id: UUID
