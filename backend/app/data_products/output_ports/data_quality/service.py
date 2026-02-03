from fastapi import HTTPException, status
from sqlalchemy import UUID, desc
from sqlalchemy.orm import Session

from app.data_products.output_ports.data_quality.enums import DataQualityStatus
from app.data_products.output_ports.data_quality.model import (
    DataQualitySummary,
    DataQualityTechnicalAsset,
)
from app.data_products.output_ports.data_quality.schema_response import (
    OutputPortDataQualitySummary,
)
from app.data_products.output_ports.model import ensure_output_port_exists


def convert_dimensions_db(
    dimensions: dict[str, DataQualityStatus] | None,
) -> dict[str, str]:
    if dimensions is None:
        return {}
    return {key: value.value for key, value in dimensions.items()}


class OutputPortDataQualityService:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_data_quality_summary(
        self, output_port_id: UUID
    ) -> DataQualitySummary:
        ensure_output_port_exists(output_port_id, self.db)

        data_quality_summary = (
            self.db.query(DataQualitySummary)
            .filter(DataQualitySummary.output_port_id == output_port_id)
            .order_by(desc(DataQualitySummary.created_at))
            .first()
        )

        if not data_quality_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data quality summary found for output port {output_port_id}",
            )
        return data_quality_summary

    def save_data_quality_summary(
        self, output_port_id: UUID, data_quality_summary: OutputPortDataQualitySummary
    ):
        ensure_output_port_exists(output_port_id, self.db)

        technical_assets = self.convert_to_db(data_quality_summary)
        assets_with_checks, assets_with_issues = self.get_asset_stats(technical_assets)

        db_summary = DataQualitySummary(
            output_port_id=output_port_id,
            details_url=data_quality_summary.details_url,
            description=data_quality_summary.description,
            created_at=data_quality_summary.created_at,
            overall_status=data_quality_summary.overall_status.value,
            dimensions=convert_dimensions_db(data_quality_summary.dimensions)
            if data_quality_summary.dimensions
            else {},
            technical_assets=technical_assets,
            assets_with_checks=assets_with_checks,
            assets_with_issues=assets_with_issues,
        )

        merged_summary = self.db.merge(db_summary)
        self.db.commit()
        return merged_summary

    def overwrite_data_quality_summary(
        self,
        output_port_id: UUID,
        summary_id: UUID,
        data_quality_summary: OutputPortDataQualitySummary,
    ) -> DataQualitySummary:
        ensure_output_port_exists(output_port_id, self.db)

        existing_summary = self.get_summary(output_port_id, summary_id)
        technical_assets = self.convert_to_db(data_quality_summary)
        assets_with_checks, assets_with_issues = self.get_asset_stats(technical_assets)

        existing_summary.details_url = data_quality_summary.details_url
        existing_summary.description = data_quality_summary.description
        existing_summary.created_at = data_quality_summary.created_at
        existing_summary.overall_status = data_quality_summary.overall_status.value
        existing_summary.dimensions = convert_dimensions_db(
            data_quality_summary.dimensions
        )
        existing_summary.assets_with_checks = assets_with_checks
        existing_summary.assets_with_issues = assets_with_issues

        # Replace collection; delete-orphan will remove old rows
        existing_summary.technical_assets = technical_assets

        self.db.commit()
        self.db.refresh(existing_summary)
        return existing_summary

    def get_summary(self, output_port_id: UUID, summary_id: UUID) -> DataQualitySummary:
        existing_summary = (
            self.db.query(DataQualitySummary)
            .filter(
                DataQualitySummary.id == summary_id,
                DataQualitySummary.output_port_id == output_port_id,
            )
            .first()
        )

        if not existing_summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Data quality summary {summary_id} not found for output port {output_port_id}",
            )
        return existing_summary

    @staticmethod
    def convert_to_db(
        data_quality_summary: OutputPortDataQualitySummary,
    ) -> list[DataQualityTechnicalAsset]:
        return [
            DataQualityTechnicalAsset(name=asset.name, status=asset.status.value)
            for asset in data_quality_summary.technical_assets
        ]

    @staticmethod
    def get_asset_stats(
        technical_assets: list[DataQualityTechnicalAsset],
    ) -> tuple[int, int]:
        assets_with_checks = len(
            [a for a in technical_assets if a.status not in [DataQualityStatus.UNKNOWN]]
        )
        assets_with_issues = len(
            [
                a
                for a in technical_assets
                if a.status in [DataQualityStatus.FAILURE, DataQualityStatus.ERROR]
            ]
        )
        return assets_with_checks, assets_with_issues
