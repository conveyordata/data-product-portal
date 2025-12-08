from datetime import date, timedelta
from enum import Enum
from typing import Iterable
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


class QueryStatsGranularity(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


DEFAULT_GRANULARITY = QueryStatsGranularity.WEEK
DEFAULT_DAY_RANGE = 90

MAX_CONSUMER_DATA_PRODUCTS = 5
OTHER_CONSUMER_DATA_PRODUCT_ID = UUID("00000000-0000-0000-0000-000000000000")
OTHER_CONSUMER_DATA_PRODUCT_NAME = "Other"


class DatasetQueryStatsDailyService:
    def __init__(self, db: Session):
        self.db = db

    def get_query_stats_daily(
        self,
        dataset_id: UUID,
        granularity: QueryStatsGranularity = DEFAULT_GRANULARITY,
        day_range: int = DEFAULT_DAY_RANGE,
    ) -> DatasetQueryStatsDailyResponses:
        start_date = self._start_date_from_day_range(day_range)
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

        if granularity != QueryStatsGranularity.DAY:
            response_stats = self._aggregate_by_granularity(response_stats, granularity)

        response_stats = self._group_low_volume_consumers(response_stats)
        response_stats = self._fill_missing_buckets(
            response_stats, start_date, granularity
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
        try:
            target_date = date.fromisoformat(delete_request.date)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {delete_request.date}") from e

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
    def _start_date_from_day_range(day_range: int) -> date:
        return date.today() - timedelta(days=day_range)

    def _aggregate_by_granularity(
        self,
        stats: list[DatasetQueryStatsDailyResponse],
        granularity: QueryStatsGranularity,
    ) -> list[DatasetQueryStatsDailyResponse]:
        """
        Aggregate stats by time granularity (week/month).
        Preserves the consumer_data_product_name from the first stat encountered.
        """
        aggregated: dict[tuple[date, UUID], DatasetQueryStatsDailyResponse] = {}
        for stat in stats:
            bucket_date = self._truncate_date(stat.date, granularity)
            key = (bucket_date, stat.consumer_data_product_id)

            if key in aggregated:
                aggregated[key].query_count += stat.query_count
            else:
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

    def _group_low_volume_consumers(
        self,
        stats: list[DatasetQueryStatsDailyResponse],
        limit: int = MAX_CONSUMER_DATA_PRODUCTS,
    ) -> list[DatasetQueryStatsDailyResponse]:
        if not stats:
            return stats

        consumer_totals, consumer_names = self._consumer_totals_and_names(stats)

        if len(consumer_totals) <= limit:
            return stats

        top_consumer_ids = self._top_consumer_ids(
            consumer_totals, consumer_names, limit
        )
        grouped_stats = self._merge_other_consumers(stats, top_consumer_ids)
        return sorted(
            grouped_stats,
            key=lambda stat: (
                stat.date,
                stat.consumer_data_product_name or "",
                str(stat.consumer_data_product_id),
            ),
        )

    def _consumer_totals_and_names(
        self, stats: list[DatasetQueryStatsDailyResponse]
    ) -> tuple[dict[UUID, int], dict[UUID, str | None]]:
        consumer_totals: dict[UUID, int] = {}
        consumer_names: dict[UUID, str | None] = {}

        for stat in stats:
            consumer_totals[stat.consumer_data_product_id] = (
                consumer_totals.get(stat.consumer_data_product_id, 0) + stat.query_count
            )

            if (
                stat.consumer_data_product_name is not None
                and consumer_names.get(stat.consumer_data_product_id) is None
            ):
                consumer_names[stat.consumer_data_product_id] = (
                    stat.consumer_data_product_name
                )

        return consumer_totals, consumer_names

    @staticmethod
    def _top_consumer_ids(
        consumer_totals: dict[UUID, int],
        consumer_names: dict[UUID, str | None],
        limit: int,
    ) -> set[UUID]:
        sorted_consumers = sorted(
            consumer_totals.items(),
            key=lambda item: (
                -item[1],
                consumer_names.get(item[0]) or "",
                str(item[0]),
            ),
        )
        return {consumer_id for consumer_id, _ in sorted_consumers[:limit]}

    @staticmethod
    def _merge_other_consumers(
        stats: list[DatasetQueryStatsDailyResponse],
        top_consumer_ids: set[UUID],
    ) -> list[DatasetQueryStatsDailyResponse]:
        other_by_date: dict[date, DatasetQueryStatsDailyResponse] = {}
        filtered_stats: list[DatasetQueryStatsDailyResponse] = []

        for stat in stats:
            if stat.consumer_data_product_id in top_consumer_ids:
                filtered_stats.append(stat)
                continue

            existing_other = other_by_date.get(stat.date)
            if existing_other:
                existing_other.query_count += stat.query_count
                continue

            other_by_date[stat.date] = DatasetQueryStatsDailyResponse(
                date=stat.date,
                consumer_data_product_id=OTHER_CONSUMER_DATA_PRODUCT_ID,
                query_count=stat.query_count,
                consumer_data_product_name=OTHER_CONSUMER_DATA_PRODUCT_NAME,
            )

        return filtered_stats + list(other_by_date.values())

    @staticmethod
    def _truncate_date(value: date, granularity: QueryStatsGranularity) -> date:
        """
        Truncate a date to the start of the specified granularity period.
        - DAY: returns the date as-is
        - WEEK: returns Monday of the week
        - MONTH: returns the first day of the month
        """
        if granularity == QueryStatsGranularity.DAY:
            return value
        if granularity == QueryStatsGranularity.WEEK:
            return value - timedelta(days=value.weekday())
        if granularity == QueryStatsGranularity.MONTH:
            return value.replace(day=1)
        return value

    def _fill_missing_buckets(
        self,
        stats: list[DatasetQueryStatsDailyResponse],
        range_start: date,
        granularity: QueryStatsGranularity,
    ) -> list[DatasetQueryStatsDailyResponse]:
        """
        Fill missing time buckets with zero values for all consumers.
        This ensures the frontend receives complete time series data.
        """
        # Build all buckets for the time range
        buckets = self._build_buckets(range_start, date.today(), granularity)

        if not stats:
            # If no stats, return empty list (no consumers to create buckets for)
            return stats

        # Get all unique consumers from the stats
        consumers: dict[UUID, str | None] = {}
        for stat in stats:
            if stat.consumer_data_product_id not in consumers:
                consumers[stat.consumer_data_product_id] = (
                    stat.consumer_data_product_name
                )

        # Create a map of existing data: key = (bucket_date, consumer_id)
        # Always truncate stat dates to ensure proper alignment with buckets
        # (important for DAY granularity where stats aren't pre-truncated)
        existing_data: dict[tuple[date, UUID], DatasetQueryStatsDailyResponse] = {}
        for stat in stats:
            bucket_date = self._truncate_date(stat.date, granularity)
            key = (bucket_date, stat.consumer_data_product_id)
            # Store stat with truncated date for consistency
            if stat.date != bucket_date:
                stat = DatasetQueryStatsDailyResponse(
                    date=bucket_date,
                    consumer_data_product_id=stat.consumer_data_product_id,
                    query_count=stat.query_count,
                    consumer_data_product_name=stat.consumer_data_product_name,
                )
            existing_data[key] = stat

        # Fill missing buckets with zero values
        filled_stats: list[DatasetQueryStatsDailyResponse] = []
        for bucket_date in buckets:
            for consumer_id, consumer_name in consumers.items():
                key = (bucket_date, consumer_id)
                if key in existing_data:
                    filled_stats.append(existing_data[key])
                else:
                    filled_stats.append(
                        DatasetQueryStatsDailyResponse(
                            date=bucket_date,
                            consumer_data_product_id=consumer_id,
                            query_count=0,
                            consumer_data_product_name=consumer_name,
                        )
                    )

        return sorted(
            filled_stats,
            key=lambda stat: (
                stat.date,
                stat.consumer_data_product_name or "",
                str(stat.consumer_data_product_id),
            ),
        )

    @staticmethod
    def _build_buckets(
        range_start: date, end_date: date, granularity: QueryStatsGranularity
    ) -> list[date]:
        """
        Build all time buckets for the given range and granularity.
        Returns a list of dates representing the start of each bucket period.
        """
        buckets: list[date] = []
        start = DatasetQueryStatsDailyService._align_to_granularity(
            range_start, granularity
        )
        end = DatasetQueryStatsDailyService._align_to_granularity(end_date, granularity)

        current = start
        while current <= end:
            buckets.append(current)
            current = DatasetQueryStatsDailyService._increment_date(
                current, granularity
            )

        return buckets

    @staticmethod
    def _align_to_granularity(value: date, granularity: QueryStatsGranularity) -> date:
        """
        Align a date to the start of the specified granularity period.
        """
        if granularity == QueryStatsGranularity.WEEK:
            return value - timedelta(days=value.weekday())
        if granularity == QueryStatsGranularity.MONTH:
            return value.replace(day=1)
        return value

    @staticmethod
    def _increment_date(value: date, granularity: QueryStatsGranularity) -> date:
        """
        Increment a date by one period according to the granularity.
        """
        if granularity == QueryStatsGranularity.WEEK:
            return value + timedelta(weeks=1)
        if granularity == QueryStatsGranularity.MONTH:
            # Increment month, handling year rollover
            if value.month == 12:
                return value.replace(year=value.year + 1, month=1)
            return value.replace(month=value.month + 1)
        return value + timedelta(days=1)
