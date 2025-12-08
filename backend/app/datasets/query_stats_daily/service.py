from datetime import date, timedelta
from enum import Enum
from typing import Iterable
from uuid import UUID

from sqlalchemy import Date, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.data_products.model import DataProduct
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
EMPTY_STRING_FALLBACK = ""  # Used for sorting when consumer_name is None


class DatasetQueryStatsDailyService:
    def __init__(self, db: Session):
        self.db = db

    def get_query_stats_daily(
        self,
        dataset_id: UUID,
        granularity: QueryStatsGranularity = DEFAULT_GRANULARITY,
        day_range: int = DEFAULT_DAY_RANGE,
    ) -> DatasetQueryStatsDailyResponses:
        start_date = date.today() - timedelta(days=day_range)

        # Build query with database-level aggregation if needed
        if granularity == QueryStatsGranularity.DAY:
            # No aggregation needed, fetch raw data
            query = (
                select(DatasetQueryStatsDaily)
                .where(
                    DatasetQueryStatsDaily.dataset_id == dataset_id,
                    DatasetQueryStatsDaily.date >= start_date,
                )
                .order_by(DatasetQueryStatsDaily.date.asc())
            )
            stats = self.db.execute(query).scalars().all()
            response_stats = [
                DatasetQueryStatsDailyResponse.model_validate(stat) for stat in stats
            ]
        else:
            # Aggregate in database using date_trunc
            trunc_unit = granularity.value  # 'week' or 'month'

            # Build aggregated query with database-level aggregation
            # Cast date_trunc result to date for cleaner handling
            truncated_date = func.date_trunc(trunc_unit, DatasetQueryStatsDaily.date)
            aggregated_query = (
                select(
                    func.cast(truncated_date, Date).label("date"),
                    DatasetQueryStatsDaily.consumer_data_product_id,
                    func.sum(DatasetQueryStatsDaily.query_count).label("query_count"),
                    DataProduct.name.label("consumer_data_product_name"),
                )
                .join(
                    DataProduct,
                    DataProduct.id == DatasetQueryStatsDaily.consumer_data_product_id,
                )
                .where(
                    DatasetQueryStatsDaily.dataset_id == dataset_id,
                    DatasetQueryStatsDaily.date >= start_date,
                )
                .group_by(
                    truncated_date,
                    DatasetQueryStatsDaily.consumer_data_product_id,
                    DataProduct.name,
                )
                .order_by(
                    truncated_date.asc(),
                    DataProduct.name.asc(),
                    DatasetQueryStatsDaily.consumer_data_product_id.asc(),
                )
            )

            results = self.db.execute(aggregated_query).all()
            response_stats = [
                DatasetQueryStatsDailyResponse(
                    date=row.date,
                    consumer_data_product_id=row.consumer_data_product_id,
                    query_count=row.query_count,
                    consumer_data_product_name=row.consumer_data_product_name,
                )
                for row in results
            ]

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
    def _sort_stats_by_date_and_consumer(
        stats: list[DatasetQueryStatsDailyResponse],
    ) -> list[DatasetQueryStatsDailyResponse]:
        """Sort stats by date, then consumer name, then consumer ID."""
        return sorted(
            stats,
            key=lambda stat: (
                stat.date,
                stat.consumer_data_product_name or EMPTY_STRING_FALLBACK,
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
        return self._sort_stats_by_date_and_consumer(grouped_stats)

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
                consumer_names.get(item[0]) or EMPTY_STRING_FALLBACK,
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
        if not stats:
            return stats

        buckets = self._build_buckets(range_start, date.today(), granularity)
        consumers = self._extract_unique_consumers(stats)
        existing_data = self._build_existing_data_map(stats, granularity)

        filled_stats = self._create_filled_buckets(buckets, consumers, existing_data)

        return self._sort_stats_by_date_and_consumer(filled_stats)

    def _extract_unique_consumers(
        self, stats: list[DatasetQueryStatsDailyResponse]
    ) -> dict[UUID, str | None]:
        """Extract all unique consumers from stats."""
        consumers: dict[UUID, str | None] = {}
        for stat in stats:
            if stat.consumer_data_product_id not in consumers:
                consumers[stat.consumer_data_product_id] = (
                    stat.consumer_data_product_name
                )
        return consumers

    def _build_existing_data_map(
        self,
        stats: list[DatasetQueryStatsDailyResponse],
        granularity: QueryStatsGranularity,
    ) -> dict[tuple[date, UUID], DatasetQueryStatsDailyResponse]:
        """
        Build a map of existing data with truncated dates.
        Key: (bucket_date, consumer_id)
        """
        existing_data: dict[tuple[date, UUID], DatasetQueryStatsDailyResponse] = {}
        for stat in stats:
            bucket_date = self._align_to_granularity(stat.date, granularity)
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

        return existing_data

    def _create_filled_buckets(
        self,
        buckets: list[date],
        consumers: dict[UUID, str | None],
        existing_data: dict[tuple[date, UUID], DatasetQueryStatsDailyResponse],
    ) -> list[DatasetQueryStatsDailyResponse]:
        """Fill missing buckets with zero values for all consumers."""
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
        return filled_stats

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
