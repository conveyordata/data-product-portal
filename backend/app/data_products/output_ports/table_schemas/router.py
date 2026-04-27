from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.table_schemas.schema_request import (
    TableSchemaRequest,
)
from app.data_products.output_ports.table_schemas.schema_response import (
    TableSchemaResponse,
)
from app.data_products.output_ports.table_schemas.service import TableSchemaService
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Table Schemas"])
base_route = "/v2/data_products/{data_product_id}/output_ports/{id}"


@router.get(f"{base_route}/table-schemas")
def get_output_port_table_schemas(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> list[TableSchemaResponse]:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return TableSchemaService(db).get_all(id)


@router.post(
    f"{base_route}/table-schemas",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def create_output_port_table_schema(
    data_product_id: UUID,
    id: UUID,
    request: TableSchemaRequest,
    db: Session = Depends(get_db_session),
) -> TableSchemaResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return TableSchemaService(db).create(id, request)


@router.put(
    f"{base_route}/table-schemas/{{schema_id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def replace_output_port_table_schema(
    data_product_id: UUID,
    id: UUID,
    schema_id: UUID,
    request: TableSchemaRequest,
    db: Session = Depends(get_db_session),
) -> TableSchemaResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return TableSchemaService(db).replace(schema_id, request)


@router.delete(
    f"{base_route}/table-schemas/{{schema_id}}",
    status_code=204,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def delete_output_port_table_schema(
    data_product_id: UUID,
    id: UUID,
    schema_id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    TableSchemaService(db).delete(schema_id)
