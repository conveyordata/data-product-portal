from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.curated_queries.schema_request import (
    DatasetCuratedQueriesUpdate,
)
from app.data_products.output_ports.curated_queries.schema_response import (
    DatasetCuratedQueries,
)
from app.data_products.output_ports.curated_queries.service import (
    DatasetCuratedQueryService,
)
from app.database.database import get_db_session

router = APIRouter(prefix="/{id}/usage/curated_queries", tags=["datasets"])


@router.get("")
def get_dataset_curated_queries(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> DatasetCuratedQueries:
    return DatasetCuratedQueryService(db).get_curated_queries(id)


@router.put(
    "",
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
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def replace_dataset_curated_queries(
    id: UUID,
    curated_queries: DatasetCuratedQueriesUpdate,
    db: Session = Depends(get_db_session),
) -> DatasetCuratedQueries:
    return DatasetCuratedQueryService(db).replace_curated_queries(
        id, curated_queries.curated_queries
    )
