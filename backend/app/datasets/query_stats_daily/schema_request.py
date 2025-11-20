from uuid import UUID

from app.shared.schema import ORMModel


class DatasetQueryStatsDailyUpdate(ORMModel):
    date: str
    consumer_data_product_id: UUID
    query_count: int


class DatasetQueryStatsDailyUpdates(ORMModel):
    dataset_query_stats_daily_updates: list[DatasetQueryStatsDailyUpdate]
