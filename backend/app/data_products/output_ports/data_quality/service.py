from fastapi import HTTPException, status
from sqlalchemy import UUID, desc
from sqlalchemy.orm import Session

from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.data_quality.model import (
    DataQualitySummary,
    DataQualityTechnicalAssetModel,
)
from app.data_products.output_ports.data_quality.schema_response import (
    OutputPortDataQualitySummary,
)
from app.data_products.output_ports.model import ensure_dataset_exists


class DatasetDataQualityService:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_data_quality_summary(self, dataset_id: UUID) -> DataQualitySummary:
        ensure_dataset_exists(dataset_id, self.db)

        data_quality_summary = (
            self.db.query(DataQualitySummary)
            .filter(DataQualitySummary.output_port_id == dataset_id)
            .order_by(desc(DataQualitySummary.created_at))
            .first()
        )

        if not data_quality_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data quality summary found for output port {dataset_id}",
            )
        return data_quality_summary

    def save_data_quality_summary(
        self, dataset_id: UUID, data_quality_summary: OutputPortDataQualitySummary
    ):
        ensure_dataset_exists(dataset_id, self.db)

        technical_assets = [
            DataQualityTechnicalAssetModel(name=asset.name, status=asset.status)
            for asset in data_quality_summary.technical_assets
        ]

        assets_with_checks = len(
            [a for a in technical_assets if a.status not in [DataQualityStatus.UNKNOWN]]
        )
        assets_with_issues = len(
            [
                a
                for a in technical_assets
                if a.status in [DataQualityStatus.FAIL, DataQualityStatus.ERROR]
            ]
        )

        db_summary = DataQualitySummary(
            output_port_id=dataset_id,
            details_url=data_quality_summary.details_url,
            description=data_quality_summary.description,
            created_at=data_quality_summary.created_at,
            overall_status=data_quality_summary.overall_status,
            dimensions=data_quality_summary.dimensions,
            technical_assets=technical_assets,
            assets_with_checks=assets_with_checks,
            assets_with_issues=assets_with_issues,
        )

        merged_summary = self.db.merge(db_summary)
        self.db.commit()
        return merged_summary
