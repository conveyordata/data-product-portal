from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.data_products.output_ports.model import ensure_dataset_exists
from app.data_products.output_ports.query_stats.schema_request import (
    DatasetQueryStatsUpdates,
    OutputPortQueryStatsDelete,
    UpdateOutputPortQueryStatus,
)
from app.data_products.output_ports.query_stats.schema_response import (
    DatasetQueryStatsResponses,
    OutputPortQueryStatsResponses,
)
from app.data_products.output_ports.query_stats.service import (
    DEFAULT_DAY_RANGE,
    OutputPortStatsService,
    QueryStatsGranularity,
)
from app.database.database import get_db_session

router = APIRouter()
old_route = "/datasets/{id}/query_stats"
route = "/v2/data_products/{data_product_id}/output_ports/{id}/query_stats"


@router.get(old_route)
def get_dataset_query_stats(
    id: UUID,
    granularity: QueryStatsGranularity = Query(default=QueryStatsGranularity.WEEK),
    day_range: int = Query(default=DEFAULT_DAY_RANGE, ge=1),
    db: Session = Depends(get_db_session),
) -> DatasetQueryStatsResponses:
    ds = ensure_dataset_exists(id, db)
    return DatasetQueryStatsResponses(
        dataset_query_stats_daily_responses=get_output_port_query_stats(
            ds.data_product_id, ds.id, granularity, day_range, db
        ).output_port_query_stats_responses
    )


@router.get(route)
def get_output_port_query_stats(
    data_product_id: UUID,
    id: UUID,
    granularity: QueryStatsGranularity = Query(default=QueryStatsGranularity.WEEK),
    day_range: int = Query(default=DEFAULT_DAY_RANGE, ge=1),
    db: Session = Depends(get_db_session),
) -> OutputPortQueryStatsResponses:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    return OutputPortStatsService(db).get_query_stats(
        dataset_id=ds.id, granularity=granularity, day_range=day_range
    )


@router.patch(old_route, deprecated=True)
def update_dataset_query_stats(
    id: UUID,
    input_data: DatasetQueryStatsUpdates,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_dataset_exists(id, db)
    update_output_port_query_stats(
        ds.data_product_id,
        ds.id,
        UpdateOutputPortQueryStatus(
            output_port_query_stats_updates=input_data.dataset_query_stats_daily_updates
        ),
        db,
    )


@router.patch(route)
def update_output_port_query_stats(
    data_product_id: UUID,
    id: UUID,
    input_data: UpdateOutputPortQueryStatus,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    OutputPortStatsService(db).update_query_stats(
        dataset_id=ds.id, updates=input_data.output_port_query_stats_updates
    )


@router.delete(old_route, deprecated=True)
def delete_dataset_query_stat(
    id: UUID,
    input_data: OutputPortQueryStatsDelete,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_dataset_exists(id, db)
    delete_output_port_query_stat(ds.data_product_id, ds.id, input_data, db)


@router.delete(route)
def delete_output_port_query_stat(
    data_product_id: UUID,
    id: UUID,
    input_data: OutputPortQueryStatsDelete,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    OutputPortStatsService(db).delete_query_stats(
        dataset_id=ds.id, delete_request=input_data
    )
