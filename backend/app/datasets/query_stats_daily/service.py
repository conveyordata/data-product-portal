from datetime import date, timedelta
from typing import Iterable, Literal
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.datasets.query_stats_daily.model import DatasetQueryStatsDaily
from app.datasets.query_stats_daily.schema_request import (
    DatasetQueryStatsDailyDelete,
    DatasetQueryStatsDailyUpdate,
)
from app.datasets.query_stats_daily.schema_response import (
    DatasetQueryStatsDailyResponse,
    DatasetQueryStatsDailyResponses,
)

GranularityLiteral = Literal["day", "week", "month"]
TimeRangeLiteral = Literal["1m", "90d", "1y"]

DEFAULT_GRANULARITY: GranularityLiteral = "week"
DEFAULT_TIME_RANGE: TimeRangeLiteral = "90d"

TIME_RANGE_TO_DAYS: dict[TimeRangeLiteral, int] = {
    "1m": 30,
    "90d": 90,
    "1y": 365,
}


class DatasetQueryStatsDailyService:
    def __init__(self, db: Session):
        self.db = db

    def get_query_stats_daily(
        self,
        dataset_id: UUID,
        granularity: GranularityLiteral = DEFAULT_GRANULARITY,
        time_range: TimeRangeLiteral = DEFAULT_TIME_RANGE,
    ) -> DatasetQueryStatsDailyResponses:
        if granularity not in {"day", "week", "month"}:
            granularity = DEFAULT_GRANULARITY
        if time_range not in TIME_RANGE_TO_DAYS:
            time_range = DEFAULT_TIME_RANGE

        start_date = self._start_date_from_range(time_range)
        stats = (
            self.db.query(DatasetQueryStatsDaily)
            .filter(
                DatasetQueryStatsDaily.dataset_id == dataset_id,
                DatasetQueryStatsDaily.date >= start_date,
            )
            .order_by(DatasetQueryStatsDaily.date.asc())
            .all()
        )
        response_stats = [
            DatasetQueryStatsDailyResponse.model_validate(stat) for stat in stats
        ]

        if granularity != "day":
            response_stats = self._aggregate_by_granularity(
                response_stats, granularity
            )

        return DatasetQueryStatsDailyResponses(
            dataset_query_stats_daily_responses=response_stats
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

    def delete_query_stats_daily(
        self, dataset_id: UUID, delete_request: DatasetQueryStatsDailyDelete
    ) -> None:
        target_date = date.fromisoformat(delete_request.date)

        (
            self.db.query(DatasetQueryStatsDaily)
            .filter(
                DatasetQueryStatsDaily.dataset_id == dataset_id,
                DatasetQueryStatsDaily.consumer_data_product_id
                == delete_request.consumer_data_product_id,
                DatasetQueryStatsDaily.date == target_date,
            )
            .delete(synchronize_session=False)
        )
        self.db.commit()
        
    @staticmethod
    def _start_date_from_range(time_range: TimeRangeLiteral) -> date:
        delta_days = TIME_RANGE_TO_DAYS.get(
            time_range, TIME_RANGE_TO_DAYS[DEFAULT_TIME_RANGE]
        )
        return date.today() - timedelta(days=delta_days)

    def _aggregate_by_granularity(
        self,
        stats: list[DatasetQueryStatsDailyResponse],
        granularity: GranularityLiteral,
    ) -> list[DatasetQueryStatsDailyResponse]:
        aggregated: dict[tuple[date, UUID], DatasetQueryStatsDailyResponse] = {}
        for stat in stats:
            bucket_date = self._truncate_date(stat.date, granularity)
            key = (bucket_date, stat.consumer_data_product_id)
            existing = aggregated.get(key)
            if existing:
                existing.query_count += stat.query_count
                continue
            aggregated[key] = DatasetQueryStatsDailyResponse(
                date=bucket_date,
                consumer_data_product_id=stat.consumer_data_product_id,
                query_count=stat.query_count,
                consumer_data_product_name=stat.consumer_data_product_name,
            )

        return sorted(
            aggregated.values(),
            key=lambda stat: (
                stat.date,
                stat.consumer_data_product_name or "",
                str(stat.consumer_data_product_id),
            ),
        )

    @staticmethod
    def _truncate_date(value: date, granularity: GranularityLiteral) -> date:
        if granularity == "day":
            return value

        if granularity == "week":
            return value - timedelta(days=value.weekday())

        if granularity == "month":
            return value.replace(day=1)

        return value
