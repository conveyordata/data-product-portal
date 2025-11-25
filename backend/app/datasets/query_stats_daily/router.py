from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.datasets.query_stats_daily.schema_request import (
    DatasetQueryStatsDailyDelete,
    DatasetQueryStatsDailyUpdates,
)
from app.datasets.query_stats_daily.schema_response import (
    DatasetQueryStatsDailyResponses,
)
from app.datasets.query_stats_daily.service import DatasetQueryStatsDailyService

router = APIRouter(prefix="/{id}/query_stats", tags=["datasets"])


@router.get("", response_model=DatasetQueryStatsDailyResponses)
def get_query_stats(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> DatasetQueryStatsDailyResponses:
    service = DatasetQueryStatsDailyService(db)
    return service.get_query_stats_daily(dataset_id=id)


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
