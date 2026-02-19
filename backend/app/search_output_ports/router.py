from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.data_products.output_ports.service import OutputPortService
from app.database.database import get_db_session
from app.search_output_ports.schema_response import (
    SearchDatasets,
    SearchOutputPortsResponse,
)
from app.users.model import User

router = APIRouter(tags=["Search Output ports"])


@router.get("/v2/search/output_ports")
def search_output_ports(
    query: Annotated[str | None, Query(min_length=3)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    current_user_assigned: bool = False,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> SearchOutputPortsResponse:
    return SearchOutputPortsResponse(
        output_ports=[
            SearchDatasets.model_validate(ds).convert()
            for ds in search_data_sets(query, limit, current_user_assigned, db, user)
        ]
    )


@router.get("/datasets/search", deprecated=True)
def search_data_sets(
    query: Annotated[str | None, Query(min_length=3)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    current_user_assigned: bool = False,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[SearchDatasets]:
    return OutputPortService(db).search_datasets(
        query=query, limit=limit, user=user, current_user_assigned=current_user_assigned
    )
