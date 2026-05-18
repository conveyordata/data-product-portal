from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.contract.schema_request import BitolContractRequest
from app.data_products.output_ports.contract.schema_response import (
    OutputPortSchemaResponse,
)
from app.data_products.output_ports.contract.service import OutputPortContractService
from app.data_products.output_ports.model import ensure_output_port_exists
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Contract"])
route = "/v2/data_products/{data_product_id}/output_ports/{id}/data_contract"


@router.get(
    route,
    responses={
        404: {
            "description": "Output Port not found",
            "content": {
                "application/json": {"example": {"detail": "Output Port ID not found"}}
            },
        }
    },
)
def get_output_port_schema(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> OutputPortSchemaResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortContractService(db).get_schema(ds.id)


@router.post(
    route,
    responses={
        404: {
            "description": "Output Port not found",
            "content": {
                "application/json": {"example": {"detail": "Output Port ID not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_CONTRACT, DatasetResolver)
        ),
    ],
)
def ingest_output_port_contract(
    data_product_id: UUID,
    id: UUID,
    contract: BitolContractRequest,
    db: Session = Depends(get_db_session),
) -> OutputPortSchemaResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortContractService(db).ingest_contract(ds.id, contract)
