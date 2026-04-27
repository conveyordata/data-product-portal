from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.data_products.output_ports.freshness.model import (
    FreshnessObservation,
    FreshnessSlo,
)
from app.data_products.output_ports.freshness.schema_request import (
    FreshnessObservationRequest,
    FreshnessSloRequest,
)
from app.data_products.output_ports.model import Dataset


class FreshnessService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_slo(
        self, output_port_id: UUID, request: FreshnessSloRequest
    ) -> FreshnessSlo:
        existing = (
            self.db.query(FreshnessSlo)
            .filter(FreshnessSlo.output_port_id == output_port_id)
            .first()
        )
        if existing:
            existing.deadline_time = request.deadline_time
            existing.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        slo = FreshnessSlo(
            output_port_id=output_port_id,
            deadline_time=request.deadline_time,
        )
        self.db.add(slo)
        self.db.commit()
        self.db.refresh(slo)
        return slo

    def get_slo(self, output_port_id: UUID) -> FreshnessSlo:
        slo = (
            self.db.query(FreshnessSlo)
            .filter(FreshnessSlo.output_port_id == output_port_id)
            .first()
        )
        if not slo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No freshness SLO configured for output port {output_port_id}",
            )
        return slo

    def delete_slo(self, output_port_id: UUID) -> None:
        slo = (
            self.db.query(FreshnessSlo)
            .filter(FreshnessSlo.output_port_id == output_port_id)
            .first()
        )
        if not slo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No freshness SLO configured for output port {output_port_id}",
            )
        self.db.delete(slo)
        self.db.commit()

    def add_observation(
        self, output_port_id: UUID, request: FreshnessObservationRequest
    ) -> FreshnessObservation:
        obs = FreshnessObservation(
            output_port_id=output_port_id,
            last_refreshed_at=request.last_refreshed_at,
        )
        self.db.add(obs)
        self.db.commit()
        self.db.refresh(obs)
        return obs

    def get_latest_observation(
        self, output_port_id: UUID
    ) -> FreshnessObservation | None:
        return (
            self.db.query(FreshnessObservation)
            .filter(FreshnessObservation.output_port_id == output_port_id)
            .order_by(desc(FreshnessObservation.last_refreshed_at))
            .first()
        )

    def compute_status(self, dataset: Dataset) -> FreshnessStatus:
        raw = dataset.freshness_status
        if raw is None:
            return FreshnessStatus.UNKNOWN
        return FreshnessStatus(raw)
