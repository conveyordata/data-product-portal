from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.data_products.output_ports.query_stats_daily.schema_request import (
    DatasetQueryStatsDailyDelete,
    DatasetQueryStatsDailyUpdates,
)
from app.data_products.output_ports.query_stats_daily.schema_response import (
    DatasetQueryStatsDailyResponses,
)
from app.data_products.output_ports.query_stats_daily.service import (
    DEFAULT_DAY_RANGE,
    DatasetQueryStatsDailyService,
    QueryStatsGranularity,
)
from app.database.database import get_db_session

router = APIRouter(prefix="/{id}/query_stats", tags=["datasets"])


@router.get("")
def get_query_stats(
    id: UUID,
    granularity: QueryStatsGranularity = Query(default=QueryStatsGranularity.WEEK),
    day_range: int = Query(default=DEFAULT_DAY_RANGE, ge=1),
    db: Session = Depends(get_db_session),
) -> DatasetQueryStatsDailyResponses:
    service = DatasetQueryStatsDailyService(db)
    return service.get_query_stats_daily(
        dataset_id=id, granularity=granularity, day_range=day_range
    )


@router.patch("")
def update_query_stats(
    id: UUID,
    input_data: DatasetQueryStatsDailyUpdates,
    db: Session = Depends(get_db_session),
) -> None:
    service = DatasetQueryStatsDailyService(db)
    service.update_query_stats_daily(
        dataset_id=id, updates=input_data.dataset_query_stats_daily_updates
    )


@router.delete("")
def delete_query_stat(
    id: UUID,
    input_data: DatasetQueryStatsDailyDelete,
    db: Session = Depends(get_db_session),
) -> None:
    service = DatasetQueryStatsDailyService(db)
    service.delete_query_stats_daily(dataset_id=id, delete_request=input_data)
