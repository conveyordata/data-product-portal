from typing import Iterable
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.datasets.query_stats_daily.model import DatasetQueryStatsDaily
from app.datasets.query_stats_daily.schema_request import DatasetQueryStatsDailyUpdate
from app.datasets.query_stats_daily.schema_response import (
    DatasetQueryStatsDailyResponses,
)


class DatasetQueryStatsDailyService:
    def __init__(self, db: Session):
        self.db = db

    def get_query_stats_daily(
        self, dataset_id: UUID
    ) -> DatasetQueryStatsDailyResponses:
        return (
            self.db.query(DatasetQueryStatsDaily)
            .filter(DatasetQueryStatsDaily.dataset_id == dataset_id)
            .all()
        )

    def update_query_stats_daily(
        self, dataset_id: UUID, updates: Iterable[DatasetQueryStatsDailyUpdate]
    ) -> None:
        values = [
            {
                "date": update.date,
                "dataset_id": dataset_id,
                "consumer_data_product_id": update.consumer_data_product_id,
                "query_count": update.query_count,
            }
            for update in updates
        ]

        if not values:
            return

        stmt = insert(DatasetQueryStatsDaily).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["date", "dataset_id", "consumer_data_product_id"],
            set_={"query_count": stmt.excluded.query_count},
        )
        self.db.execute(stmt)
        self.db.commit()
