from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import Dataset
from app.database.database import get_db_session
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
    data_product_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db_session),
) -> ResourceNameValidation:
    scope: Optional[UUID | DataProductSettingScope] = None
    if model == ResourceNameModel.DATA_PRODUCT:
        service = ResourceNameService(model=DataProduct)
    elif model == ResourceNameModel.TECHNICAL_ASSET:
        service = DataOutputResourceNameValidator()
        scope = data_product_id
    elif model == ResourceNameModel.OUTPUT_PORT:
        service = ResourceNameService(model=Dataset)
    elif model == ResourceNameModel.DATA_PRODUCT_SETTING:
        service = DataProductSettingResourceNameValidator()
        scope = DataProductSettingScope.DATAPRODUCT
    elif model == ResourceNameModel.OUTPUT_PORT_SETTING:
        service = DataProductSettingResourceNameValidator()
        scope = DataProductSettingScope.DATASET

    return service.validate_resource_name(resource_name, db, scope=scope)


@router.get("/constraints")
def resource_name_constraints() -> ResourceNameLengthLimits:
    return ResourceNameService.resource_name_length_limits()
