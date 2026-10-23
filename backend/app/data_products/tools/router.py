from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DataProductResolver
from app.data_products.tools.schema_request import (
    CreateToolRequest,
    UpdateToolEnvironmentConfigurationRequest,
)
from app.data_products.tools.schema_response import (
    CreateToolResponse,
    GetToolsResponse,
    Tool,
    ToolEnvironmentConfiguration,
)
from app.data_products.tools.service import ToolService
from app.database.deps import get_db_session

router = APIRouter(
    tags=["Data Products - Tools"],
    prefix="/v2/data_products/{data_product_id}/tools",
)

read_dependency = Depends(
    Authorization.enforce(
        Action.HIDDEN__DATA_PRODUCT__READ,
        DataProductResolver,
        object_id="data_product_id",
    )
)
write_dependency = Depends(
    Authorization.enforce(
        Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
        DataProductResolver,
        object_id="data_product_id",
    )
)


@router.get("", dependencies=[read_dependency])
def get_data_product_tools(
    data_product_id: UUID, db: Session = Depends(get_db_session, scope="function")
) -> GetToolsResponse:
    return GetToolsResponse(tools=ToolService(db).get_tools(data_product_id))


@router.post("", dependencies=[write_dependency])
def create_tool(
    data_product_id: UUID,
    request: CreateToolRequest,
    db: Session = Depends(get_db_session, scope="function"),
) -> CreateToolResponse:
    return CreateToolResponse(
        id=ToolService(db).create_tool(data_product_id, request).id
    )


@router.get("/{id}", dependencies=[read_dependency])
def get_tool(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> Tool:
    return Tool.model_validate(ToolService(db).get_tool(data_product_id, id))


@router.delete("/{id}", dependencies=[write_dependency])
def delete_tool(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> None:
    ToolService(db).delete_tool(data_product_id, id)


@router.get("/{id}/environment-configuration", dependencies=[read_dependency])
def get_tool_environment_configuration(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> ToolEnvironmentConfiguration:
    return ToolService(db).get_environment_configuration(data_product_id, id)


@router.put("/{id}/environment-configuration", dependencies=[write_dependency])
def update_tool_environment_configuration(
    data_product_id: UUID,
    id: UUID,
    request: UpdateToolEnvironmentConfigurationRequest,
    db: Session = Depends(get_db_session, scope="function"),
) -> ToolEnvironmentConfiguration:
    return ToolService(db).update_environment_configuration(
        data_product_id, id, request
    )
