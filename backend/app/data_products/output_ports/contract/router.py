from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile

from app.core.authz import Action, Authorization, OutputPortResolver
from app.data_products.output_ports.contract.schema_request import BitolContractRequest
from app.data_products.output_ports.contract.schema_response import (
    OutputPortSchemaResponse,
)
from app.data_products.output_ports.contract.service import OutputPortContractService
from app.data_products.output_ports.model import ensure_output_port_exists
from app.database.deps import DbSession

router = APIRouter(
    tags=["Data Products - Output Ports - Contract"],
    prefix="/{id}/data_contract",
)


@router.get(
    "",
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
            Authorization.enforce(Action.HIDDEN__OUTPUT_PORT__READ, OutputPortResolver)
        )
    ],
)
def get_output_port_schema(
    data_product_id: UUID,
    id: UUID,
    db: DbSession,
) -> OutputPortSchemaResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortContractService(db).get_schema(ds.id)


@router.post(
    "",
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
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_CONTRACT, OutputPortResolver
            )
        ),
    ],
)
def ingest_output_port_contract(
    data_product_id: UUID,
    id: UUID,
    contract: BitolContractRequest,
    db: DbSession,
) -> OutputPortSchemaResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortContractService(db).ingest_contract(ds.id, contract)


@router.post(
    "/upload",
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
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_CONTRACT, OutputPortResolver
            )
        ),
    ],
)
def ingest_output_port_contract_yaml(
    data_product_id: UUID,
    id: UUID,
    file: Annotated[UploadFile, File()],
    db: DbSession,
) -> OutputPortSchemaResponse:
    contract = OutputPortContractService.parse_contract_yaml(file.file.read())
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return OutputPortContractService(db).ingest_contract(ds.id, contract)
