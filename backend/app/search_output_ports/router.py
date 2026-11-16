from typing import Annotated

from fastapi import APIRouter, Query
from pydantic.json_schema import SkipJsonSchema

from app.authorization.role_assignments.enums import AssignmentFilter
from app.core.auth.auth import AuthenticatedUser
from app.data_products.output_ports.service import OutputPortService
from app.database.deps import DbSession
from app.search_output_ports.schema_response import (
    SearchOutputPortsResponse,
    SearchOutputPortsResponseItem,
)

router = APIRouter(tags=["Search Output ports"])


@router.get("/v2/search/output_ports")
def search_output_ports(
    db: DbSession,
    user: AuthenticatedUser,
    query: Annotated[str | SkipJsonSchema[None], Query(min_length=3)] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    assignment_filter: AssignmentFilter = AssignmentFilter.ALL,
) -> SearchOutputPortsResponse:
    return SearchOutputPortsResponse(
        output_ports=[
            SearchOutputPortsResponseItem.model_validate(ds)
            for ds in OutputPortService(db).search_output_ports(
                query=query,
                limit=limit,
                user=user,
                assignment_filter=assignment_filter,
            )
        ]
    )
