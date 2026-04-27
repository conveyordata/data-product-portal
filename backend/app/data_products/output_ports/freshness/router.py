from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization, DatasetResolver
from app.data_products.output_ports.freshness.model import (
    FreshnessObservation,
    FreshnessSlo,
)
from app.data_products.output_ports.freshness.schema_request import (
    FreshnessObservationRequest,
    FreshnessSloRequest,
)
from app.data_products.output_ports.freshness.schema_response import (
    FreshnessObservationResponse,
    FreshnessSloResponse,
)
from app.data_products.output_ports.freshness.service import FreshnessService
from app.data_products.output_ports.model import ensure_output_port_exists
from app.database.database import get_db_session

router = APIRouter(tags=["Data Products - Output Ports - Freshness"])
base_route = "/v2/data_products/{data_product_id}/output_ports/{id}"


def _to_slo_response(
    slo: FreshnessSlo,
    dataset,
    latest_obs: FreshnessObservation | None,
    service: FreshnessService,
) -> FreshnessSloResponse:
    return FreshnessSloResponse(
        id=slo.id,
        output_port_id=slo.output_port_id,
        deadline_time=slo.deadline_time,
        status=service.compute_status(dataset),
        last_refreshed_at=latest_obs.last_refreshed_at if latest_obs else None,
        last_observed_at=latest_obs.created_at if latest_obs else None,
    )


@router.get(f"{base_route}/freshness_slo")
def get_freshness_slo(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> FreshnessSloResponse:
    dataset = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    service = FreshnessService(db)
    slo = service.get_slo(id)
    latest_obs = service.get_latest_observation(id)
    return _to_slo_response(slo, dataset, latest_obs, service)


@router.put(
    f"{base_route}/freshness_slo",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def upsert_freshness_slo(
    data_product_id: UUID,
    id: UUID,
    request: FreshnessSloRequest,
    db: Session = Depends(get_db_session),
) -> FreshnessSloResponse:
    dataset = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    service = FreshnessService(db)
    slo = service.upsert_slo(id, request)
    db.refresh(dataset)
    latest_obs = service.get_latest_observation(id)
    return _to_slo_response(slo, dataset, latest_obs, service)


@router.delete(
    f"{base_route}/freshness_slo",
    status_code=204,
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        )
    ],
)
def delete_freshness_slo(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    FreshnessService(db).delete_slo(id)


@router.post(
    f"{base_route}/freshness_observations",
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_FRESHNESS, DatasetResolver)
        )
    ],
)
def add_freshness_observation(
    data_product_id: UUID,
    id: UUID,
    request: FreshnessObservationRequest,
    db: Session = Depends(get_db_session),
) -> FreshnessObservationResponse:
    dataset = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    service = FreshnessService(db)
    obs = service.add_observation(id, request)
    db.refresh(dataset)
    return FreshnessObservationResponse(
        id=obs.id,
        output_port_id=obs.output_port_id,
        last_refreshed_at=obs.last_refreshed_at,
        created_at=obs.created_at,
        status=service.compute_status(dataset),
    )
