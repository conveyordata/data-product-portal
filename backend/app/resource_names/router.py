from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic.json_schema import SkipJsonSchema

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.configuration.domains.model import Domain
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import OutputPort
from app.database.deps import DbSession
from app.explorations.model import Exploration
from app.resource_names.enums import ResourceNameModel
from app.resource_names.service import (
    DataOutputResourceNameValidator,
    DataProductSettingResourceNameValidator,
    ResourceNameLengthLimits,
    ResourceNameService,
    ResourceNameSuggestion,
    ResourceNameValidation,
)

router = APIRouter(tags=["Resource names"], prefix="/v2/resource_names")


@router.get("/sanitize")
def sanitize_resource_name(
    name: str, technical_asset_type: str | None = None
) -> ResourceNameSuggestion:
    max_length = (
        DataOutputResourceNameValidator(technical_asset_type).max_length
        if technical_asset_type is not None
        else None
    )
    return ResourceNameService.resource_name_suggestion(name, max_length)


@router.get("/validate")
def validate_resource_name(
    resource_name: str,
    model: ResourceNameModel,
    db: DbSession,
    data_product_id: Annotated[UUID | SkipJsonSchema[None], Query()] = None,
    technical_asset_type: str | None = None,
) -> ResourceNameValidation:
    match model:
        case ResourceNameModel.DATA_PRODUCT:
            return ResourceNameService(model=DataProduct).validate_resource_name(
                resource_name, db
            )
        case ResourceNameModel.TECHNICAL_ASSET:
            if technical_asset_type is None or data_product_id is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="technical_asset_type and data_product_id are required for Technical Assets",
                )
            return DataOutputResourceNameValidator(
                technical_asset_type
            ).validate_resource_name(resource_name, db, scope=data_product_id)
        case ResourceNameModel.OUTPUT_PORT:
            return ResourceNameService(model=OutputPort).validate_resource_name(
                resource_name, db
            )
        case ResourceNameModel.DATA_PRODUCT_SETTING:
            return DataProductSettingResourceNameValidator().validate_resource_name(
                resource_name, db, DataProductSettingScope.DATAPRODUCT
            )
        case ResourceNameModel.OUTPUT_PORT_SETTING:
            return DataProductSettingResourceNameValidator().validate_resource_name(
                resource_name, db, DataProductSettingScope.DATASET
            )
        case ResourceNameModel.EXPLORATION:
            return ResourceNameService(model=Exploration).validate_resource_name(
                resource_name, db
            )
        case ResourceNameModel.DOMAIN:
            return ResourceNameService(model=Domain).validate_resource_name(
                resource_name, db
            )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid model: {}".format(model),
    )


@router.get("/constraints")
def resource_name_constraints() -> ResourceNameLengthLimits:
    return ResourceNameService.resource_name_length_limits()
