from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.curated_queries.schema_request import (
    OutputPortCuratedQueriesUpdate,
)
from app.data_products.output_ports.curated_queries.schema_response import (
    DatasetCuratedQueries,
    OutputPortCuratedQueries,
)
from app.data_products.output_ports.curated_queries.service import (
    DatasetCuratedQueryService,
)
from app.data_products.output_ports.model import ensure_dataset_exists
from app.database.database import get_db_session

router = APIRouter()
old_route = "/datasets/{id}/usage/curated_queries"
route = "/v2/data_products/{data_product_id}/output_ports/{id}/curated_queries"


@router.get(old_route, deprecated=True)
def get_dataset_curated_queries(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> DatasetCuratedQueries:
    ds = ensure_dataset_exists(id, db)
    return DatasetCuratedQueries(
        dataset_curated_queries=get_output_port_curated_queries(
            ds.data_product_id, id, db
        ).output_port_curated_queries
    )


@router.get(route)
def get_output_port_curated_queries(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> OutputPortCuratedQueries:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    return DatasetCuratedQueryService(db).get_curated_queries(ds.id)


@router.put(
    old_route,
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
    ],
    deprecated=True,
)
def replace_dataset_curated_queries(
    id: UUID,
    curated_queries: OutputPortCuratedQueriesUpdate,
    db: Session = Depends(get_db_session),
) -> DatasetCuratedQueries:
    ds = ensure_dataset_exists(id, db)
    return DatasetCuratedQueries(
        dataset_curated_queries=replace_output_port_curated_queries(
            ds.data_product_id, id, curated_queries, db
        ).output_port_curated_queries
    )


@router.put(
    route,
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
    ],
)
def replace_output_port_curated_queries(
    data_product_id: UUID,
    id: UUID,
    curated_queries: OutputPortCuratedQueriesUpdate,
    db: Session = Depends(get_db_session),
) -> OutputPortCuratedQueries:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    return DatasetCuratedQueryService(db).replace_curated_queries(
        ds.id, curated_queries.curated_queries
    )
