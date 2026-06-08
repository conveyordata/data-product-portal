from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy.orm import Session

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import Dataset
from app.database.database import get_db_session
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
def sanitize_resource_name(name: str) -> ResourceNameSuggestion:
    return ResourceNameService.resource_name_suggestion(name)


@router.get("/validate")
def validate_resource_name(
    resource_name: str,
    model: ResourceNameModel,
    data_product_id: Annotated[UUID | SkipJsonSchema[None], Query()] = None,
    db: Session = Depends(get_db_session),
) -> ResourceNameValidation:
    match model:
        case ResourceNameModel.DATA_PRODUCT:
            return ResourceNameService(model=DataProduct).validate_resource_name(
                resource_name, db
            )
        case ResourceNameModel.TECHNICAL_ASSET:
            return DataOutputResourceNameValidator().validate_resource_name(
                resource_name, db, scope=data_product_id
            )
        case ResourceNameModel.OUTPUT_PORT:
            return ResourceNameService(model=Dataset).validate_resource_name(
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
    raise HTTPException(  # noqa: unreachable
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid model: {}".format(model),
    )


@router.get("/constraints")
def resource_name_constraints() -> ResourceNameLengthLimits:
    return ResourceNameService.resource_name_length_limits()
