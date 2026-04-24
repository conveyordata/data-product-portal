from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.abstract_data_product.schema_response import InputPort
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.database.database import get_db_session
from app.explorations.model import ensure_exploration_exists
from app.explorations.schema_request import (
    CreateExplorationRequest,
    CreateExplorationRequestWithInputPorts,
)
from app.explorations.schema_response import (
    CreateExplorationResponse,
    GetExplorationInputPortsResponse,
    GetExplorationResponse,
    GetExplorationsResponse,
)
from app.explorations.service import ExplorationService
from app.users.model import User

route = "/v2/explorations"
router = APIRouter(tags=["Explorations"], prefix=route)


@router.get("", response_model=GetExplorationsResponse)
def get_explorations(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return {"explorations": ExplorationService(db).get_explorations(authenticated_user)}


@router.post(
    "",
    response_model=CreateExplorationResponse,
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_EXPLORATION, EmptyResolver))
    ],
)
def create_exploration(
    request: CreateExplorationRequestWithInputPorts,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    created_exploration = ExplorationService(db).create_exploration(
        CreateExplorationRequest(**request.model_dump(exclude={"input_ports"})),
        authenticated_user,
    )
    if request.input_ports:
        input_ports = ExplorationService(db).request_input_ports(
            created_exploration.id,
            request.input_ports.output_ports,
            request.input_ports.justification,
            actor=authenticated_user,
        )
        ExplorationService(db).send_input_port_requested_emails_to_output_port_owners(
            input_ports,
            background_tasks,
            authenticated_user,
        )
        RefreshInfrastructureLambda().trigger()
    return created_exploration


@router.get("/{id}", response_model=GetExplorationResponse)
def get_exploration(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return ExplorationService(db).get_exploration(id, authenticated_user)


@router.get("/{id}/input_ports", response_model=GetExplorationInputPortsResponse)
def get_exploration_input_ports(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    ensure_exploration_exists(id, db, authenticated_user)
    return GetExplorationInputPortsResponse(
        input_ports=[
            InputPort.model_validate(ip)
            for ip in ExplorationService(db).get_input_ports(id)
        ]
    )
