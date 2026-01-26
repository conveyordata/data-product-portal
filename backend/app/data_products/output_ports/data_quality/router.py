from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.data_quality.model import (
    DataQualitySummary,
    DataQualityTechnicalAssetModel,
)
from app.data_products.output_ports.data_quality.schema_request import (
    DataQualityTechnicalAsset,
)
from app.data_products.output_ports.data_quality.schema_response import (
    OutputPortDataQualitySummary,
    OutputPortDataQualitySummaryResponse,
)
from app.data_products.output_ports.data_quality.service import (
    DatasetDataQualityService,
)
from app.data_products.output_ports.model import ensure_dataset_exists
from app.database.database import get_db_session

router = APIRouter(tags=["Output Ports - Data Quality"])
route = "/v2/data_products/{data_product_id}/output_ports/{id}/data_quality_summary"


def convert_dimensions_to_api(
    dimensions: dict[str, str],
) -> dict[str, DataQualityStatus]:
    return {key: DataQualityStatus(value) for key, value in dimensions.items()}


def convert_technical_assets_to_api(
    technical_assets: list[DataQualityTechnicalAssetModel],
):
    return [
        DataQualityTechnicalAsset(
            name=tech_asset.name, status=DataQualityStatus(tech_asset.status)
        )
        for tech_asset in technical_assets
    ]


@router.get(route)
def get_latest_data_quality_summary_for_output_port(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> OutputPortDataQualitySummary:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    summary = DatasetDataQualityService(db).get_latest_data_quality_summary(ds.id)
    return convert(summary, id)


def convert(
    summary: DataQualitySummary, dataset_id: UUID
) -> OutputPortDataQualitySummaryResponse:
    return OutputPortDataQualitySummaryResponse(
        output_port_id=dataset_id,
        description=summary.description,
        created_at=summary.created_at,
        details_url=summary.details_url,
        dimensions=convert_dimensions_to_api(summary.dimensions),
        technical_assets=convert_technical_assets_to_api(summary.technical_assets),
        overall_status=DataQualityStatus(summary.overall_status),
        id=summary.id,
    )


@router.post(
    route,
    responses={
        404: {
            "description": "Output Port not found",
            "content": {
                "application/json": {"example": {"detail": "Output Port ID not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def add_output_port_data_quality_run(
    data_product_id: UUID,
    id: UUID,
    data_quality_summary: OutputPortDataQualitySummary,
    db: Session = Depends(get_db_session),
) -> OutputPortDataQualitySummaryResponse:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    summary_response = DatasetDataQualityService(db).save_data_quality_summary(
        ds.id, data_quality_summary
    )
    return convert(summary_response, ds.id)
