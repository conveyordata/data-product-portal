from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, OutputPortResolver
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
from app.database.deps import get_db_session

router = APIRouter(prefix="/{id}/query_stats")


@router.get(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN__OUTPUT_PORT__READ,
                OutputPortResolver,
            )
        )
    ],
)
def get_output_port_query_stats(
    data_product_id: UUID,
    id: UUID,
    granularity: QueryStatsGranularity = Query(default=QueryStatsGranularity.WEEK),
    day_range: int = Query(default=DEFAULT_DAY_RANGE, ge=1),
    db: Session = Depends(get_db_session),
) -> OutputPortQueryStatsResponses:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortStatsService(db).get_query_stats(
        output_port_id=ds.id, granularity=granularity, day_range=day_range
    )


@router.patch(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_QUERY_STATS,
                OutputPortResolver,
            )
        ),
    ],
)
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


@router.delete(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_QUERY_STATS,
                OutputPortResolver,
            )
        ),
    ],
)
def delete_output_port_query_stat(
    data_product_id: UUID,
    id: UUID,
    input_data: OutputPortQueryStatsDelete,
    db: Session = Depends(get_db_session),
) -> None:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    OutputPortStatsService(db).delete_query_stats(
        output_port_id=ds.id, delete_request=input_data
    )
