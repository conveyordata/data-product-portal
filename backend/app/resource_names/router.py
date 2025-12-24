from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import Dataset
from app.database.database import get_db_session
from app.resource_names.enums import ResourceNameModel
from app.resource_names.schema_request import ResourceNameValidationRequest
from app.resource_names.service import (
    DataOutputResourceNameValidator,
    DataProductSettingResourceNameValidator,
    ResourceNameLengthLimits,
    ResourceNameService,
    ResourceNameSuggestion,
    ResourceNameValidation,
)

if TYPE_CHECKING:
    from uuid import UUID

router = APIRouter(tags=["Resource names"], prefix="/v2/resource_names")


@router.post("/sanitize")
def sanitize_resource_name(name: str) -> ResourceNameSuggestion:
    return ResourceNameService.resource_name_suggestion(name)


@router.post("/validate")
def validate_resource_name(
    request: ResourceNameValidationRequest, db: Session = Depends(get_db_session)
) -> ResourceNameValidation:
    scope: Optional[UUID | DataProductSettingScope] = None
    if request.model == ResourceNameModel.DATA_PRODUCT:
        service = ResourceNameService(model=DataProduct)
    elif request.model == ResourceNameModel.TECHNICAL_ASSET:
        service = DataOutputResourceNameValidator()
        scope = request.data_product_id
    elif request.model == ResourceNameModel.OUTPUT_PORT:
        service = ResourceNameService(model=Dataset)
    elif request.model == ResourceNameModel.DATA_PRODUCT_SETTING:
        service = DataProductSettingResourceNameValidator()
        scope = DataProductSettingScope.DATAPRODUCT
    elif request.model == ResourceNameModel.OUTPUT_PORT_SETTING:
        service = DataProductSettingResourceNameValidator()
        scope = DataProductSettingScope.DATASET

    return service.validate_resource_name(request.resource_name, db, scope=scope)


@router.get("/constraints")
def resource_name_constraints() -> ResourceNameLengthLimits:
    return ResourceNameService.resource_name_length_limits()
