from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.cost.schema_request import CreateCostRecord
from app.data_products.output_ports.cost.schema_response import (
    CostHistoryResponse,
    CostRecordResponse,
)
from app.data_products.output_ports.cost.service import OutputPortCostService
from app.data_products.output_ports.model import ensure_output_port_exists
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Cost"])
route = "/v2/data_products/{data_product_id}/output_ports/{id}/cost"


@router.post(
    route,
    status_code=201,
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__UPDATE_COST, DatasetResolver))
    ],
)
def push_cost_record(
    data_product_id: UUID,
    id: UUID,
    record: CreateCostRecord,
    db: Session = Depends(get_db_session),
) -> CostRecordResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    result = OutputPortCostService(db).push_cost_record(ds.id, record)
    return CostRecordResponse.model_validate(result)


@router.get(route)
def get_cost_history(
    data_product_id: UUID,
    id: UUID,
    day_range: int = Query(default=90, ge=1),
    db: Session = Depends(get_db_session),
) -> CostHistoryResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    records = OutputPortCostService(db).get_cost_history(ds.id, day_range)
    return CostHistoryResponse(
        output_port_id=ds.id,
        records=[CostRecordResponse.model_validate(r) for r in records],
    )
