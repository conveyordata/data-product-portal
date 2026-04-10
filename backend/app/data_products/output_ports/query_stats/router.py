from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.query_stats.schema_request import (
    OutputPortQueryStatsDelete,
    UpdateOutputPortQueryStatus,
)
from app.data_products.output_ports.query_stats.schema_response import (
    OutputPortQueryStatsResponses,
)
from app.data_products.output_ports.query_stats.service import (
    DEFAULT_DAY_RANGE,
    OutputPortStatsService,
    QueryStatsGranularity,
)
from app.database.database import get_db_session

router = APIRouter()
route = "/v2/data_products/{data_product_id}/output_ports/{id}/query_stats"


@router.get(route)
def get_output_port_query_stats(
    data_product_id: UUID,
    id: UUID,
    granularity: QueryStatsGranularity = Query(default=QueryStatsGranularity.WEEK),
    day_range: int = Query(default=DEFAULT_DAY_RANGE, ge=1),
    db: Session = Depends(get_db_session),
) -> OutputPortQueryStatsResponses:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortStatsService(db).get_query_stats(
        dataset_id=ds.id, granularity=granularity, day_range=day_range
    )


@router.patch(route)
def update_output_port_query_stats(
    data_product_id: UUID,
    id: UUID,
    input_data: UpdateOutputPortQueryStatus,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    OutputPortStatsService(db).update_query_stats(
        dataset_id=ds.id, updates=input_data.output_port_query_stats_updates
    )


@router.delete(route)
def delete_output_port_query_stat(
    data_product_id: UUID,
    id: UUID,
    input_data: OutputPortQueryStatsDelete,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    OutputPortStatsService(db).delete_query_stats(
        dataset_id=ds.id, delete_request=input_data
    )
