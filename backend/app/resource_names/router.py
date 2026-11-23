from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic.json_schema import SkipJsonSchema

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.configuration.domains.model import Domain
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import OutputPort
from app.data_products.technical_assets.service import TechnicalAssetService
from app.database.deps import DbSession
from app.explorations.model import Exploration
from app.plugins.registry import ensure_technical_asset_type
from app.resource_names.enums import ResourceNameModel
from app.resource_names.service import (
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
    return ResourceNameService.resource_name_suggestion(name, technical_asset_type)


@router.get("/validate")
def validate_resource_name(
    resource_name: str,
    model: ResourceNameModel,
    db: DbSession,
    data_product_id: Annotated[UUID | SkipJsonSchema[None], Query()] = None,
    technical_asset_type: Annotated[str | SkipJsonSchema[None], Query()] = None,
) -> ResourceNameValidation:
    match model:
        case ResourceNameModel.DATA_PRODUCT:
            return ResourceNameService(model=DataProduct).validate_resource_name(
                resource_name, db
            )
        case ResourceNameModel.TECHNICAL_ASSET:
            if data_product_id is None or technical_asset_type is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="data_product_id and technical_asset_type are required",
                )
            try:
                ensure_technical_asset_type(technical_asset_type)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
                ) from e
            return ResourceNameValidation(
                validity=TechnicalAssetService(db).validate_namespace(
                    data_product_id, resource_name, technical_asset_type
                )
            )
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
