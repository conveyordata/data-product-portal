from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DatasetResolver
from app.database.database import get_db_session
from app.datasets.curated_queries.schema_request import DatasetCuratedQueriesUpdate
from app.datasets.curated_queries.schema_response import DatasetCuratedQuery
from app.datasets.curated_queries.service import DatasetCuratedQueryService
from app.datasets.service import DatasetService
from app.users.model import User

router = APIRouter(prefix="/{id}/usage/curated_queries", tags=["datasets"])


@router.get("")
def get_dataset_curated_queries(
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[DatasetCuratedQuery]:
    DatasetService(db).get_dataset(id, user)
    return DatasetCuratedQueryService(db).get_curated_queries(id)


@router.put(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def upsert_dataset_curated_queries(
    id: UUID,
    curated_queries: DatasetCuratedQueriesUpdate,
    db: Session = Depends(get_db_session),
) -> Sequence[DatasetCuratedQuery]:
    return DatasetCuratedQueryService(db).replace_curated_queries(
        id, curated_queries.curated_queries
    )
