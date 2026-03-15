from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.router import _assign_owner_role_assignments
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.ephemeral_access.schema_request import (
    AddOutputPortsToEphemeral,
    EphemeralDataProductCreate,
)
from app.ephemeral_access.schema_response import (
    CreateEphemeralAccessResponse,
    EphemeralAccessResponse,
    PromoteEphemeralAccessResponse,
)
from app.ephemeral_access.service import EphemeralAccessService
from app.users.schema import User

router = APIRouter(tags=["Ephemeral Access"])
route = "/v2/ephemeral_access"


@router.post(route)
def create_ephemeral_access(
    data: EphemeralDataProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateEphemeralAccessResponse:
    dp = EphemeralAccessService(db).create_ephemeral_access(data, authenticated_user)
    _assign_owner_role_assignments(
        dp.id,
        owners=[authenticated_user.id],
        db=db,
        actor=authenticated_user,
    )
    DataProductService(db).link_datasets_to_data_product(
        dp.id,
        data.output_port_ids,
        justification=data.justification or "Exploration",
        actor=authenticated_user,
    )
    return CreateEphemeralAccessResponse(id=dp.id)


@router.get(route)
def list_ephemeral_access(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[EphemeralAccessResponse]:
    items = EphemeralAccessService(db).list_ephemeral_access(authenticated_user.id)
    return [EphemeralAccessResponse.from_model(item) for item in items]


@router.post(f"{route}/{{id}}/output_ports")
def add_output_ports_to_ephemeral(
    id: UUID,
    data: AddOutputPortsToEphemeral,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    EphemeralAccessService(db).add_output_ports(
        id, data.output_port_ids, authenticated_user
    )


@router.delete(f"{route}/{{id}}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_ephemeral_access(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    EphemeralAccessService(db).revoke_ephemeral_access(id)


@router.post(f"{route}/{{id}}/promote")
def promote_ephemeral_access(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> PromoteEphemeralAccessResponse:
    data_product_id = EphemeralAccessService(db).promote_ephemeral_access(id)
    RefreshInfrastructureLambda().trigger()
    return PromoteEphemeralAccessResponse(id=data_product_id)
