from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.semantic_models.schema_request import (
    SemanticModelRequest,
)
from app.data_products.output_ports.semantic_models.schema_response import (
    SemanticModelResponse,
)
from app.data_products.output_ports.semantic_models.service import SemanticModelService
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Semantic Models"])
base_route = "/v2/data_products/{data_product_id}/output_ports/{id}"


@router.get(f"{base_route}/semantic-models")
def get_output_port_semantic_models(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> list[SemanticModelResponse]:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return SemanticModelService(db).get_all(id)


@router.post(
    f"{base_route}/semantic-models",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def create_output_port_semantic_model(
    data_product_id: UUID,
    id: UUID,
    request: SemanticModelRequest,
    db: Session = Depends(get_db_session),
) -> SemanticModelResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return SemanticModelService(db).create(id, request)


@router.put(
    f"{base_route}/semantic-models/{{model_id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def replace_output_port_semantic_model(
    data_product_id: UUID,
    id: UUID,
    model_id: UUID,
    request: SemanticModelRequest,
    db: Session = Depends(get_db_session),
) -> SemanticModelResponse:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return SemanticModelService(db).replace(model_id, request)


@router.delete(
    f"{base_route}/semantic-models/{{model_id}}",
    status_code=204,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def delete_output_port_semantic_model(
    data_product_id: UUID,
    id: UUID,
    model_id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    SemanticModelService(db).delete(model_id)
