from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import AssignmentFilter
from app.data_products.service import DataProductService
from app.database.deps import get_db_session
from app.search_data_products.schema_response import (
    SearchDataProductsResponse,
    SearchDataProductsResponseItem,
)

router = APIRouter(tags=["Search Data Products"])


@router.get("/v2/search/data_products")
def search_data_products(
    query: Annotated[str | SkipJsonSchema[None], Query(min_length=3)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    assignment_filter: AssignmentFilter = AssignmentFilter.ALL,
    db: Session = Depends(get_db_session, scope="function"),
) -> SearchDataProductsResponse:
    return SearchDataProductsResponse(
        data_products=[
            SearchDataProductsResponseItem.model_validate(dp)
            for dp in DataProductService(db).search_data_products(
                query=query,
                limit=limit,
                assignment_filter=assignment_filter,
            )
        ]
    )
