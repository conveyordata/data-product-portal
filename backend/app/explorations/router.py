from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy.orm import Session

from app.abstract_data_product.schema_request import FinalizerRequest
from app.abstract_data_product.schema_response import AbstractDataProductInputPort
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.database.database import get_db_session
from app.explorations.schema_request import (
    CreateExplorationRequest,
    CreateExplorationRequestWithInputPorts,
    RequestInputPortsForExplorationRequest,
)
from app.explorations.schema_response import (
    CancelInputPortForExplorationResponse,
    CreateExplorationResponse,
    GetExplorationInputPortsResponse,
    GetExplorationResponse,
    GetExplorationsResponse,
    RenewInputPortForExplorationResponse,
    RequestInputPortsForExplorationResponse,
    RevokeInputPortForExplorationResponse,
)
from app.explorations.service import ExplorationService
from app.users.model import User

route = "/v2/explorations"
router = APIRouter(tags=["Explorations"], prefix=route)


@router.get("", response_model=GetExplorationsResponse)
def get_explorations(
    db: Session = Depends(get_db_session),
    filter_to_user_with_assigment: Annotated[
        UUID | SkipJsonSchema[None], Query()
    ] = None,
):
    return {
        "explorations": ExplorationService(db).get_explorations(
            filter_to_user_with_assigment
        )
    }


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
):
    return GetExplorationInputPortsResponse(
        input_ports=[
            AbstractDataProductInputPort.model_validate(ip)
            for ip in ExplorationService(db).get_input_ports(id)
        ]
    )


@router.post(
    "/{id}/input_ports", response_model=RequestInputPortsForExplorationResponse
)
def request_input_ports_for_exploration(
    id: UUID,
    request: RequestInputPortsForExplorationRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    exp = ExplorationService(db).get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )

    RefreshInfrastructureLambda().trigger()
    return RequestInputPortsForExplorationResponse(
        input_port_ids=[
            ip.id
            for ip in ExplorationService(db).request_input_ports(
                id,
                request.output_ports,
                request.justification,
                actor=authenticated_user,
            )
        ]
    )


@router.post("/{id}/input_ports/{output_port_id}/renew")
def renew_input_port_for_exploration(
    id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> RenewInputPortForExplorationResponse:
    exp = ExplorationService(db).get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )

    input_port = ExplorationService(db).renew_input_port(
        id, output_port_id, actor=authenticated_user
    )
    RefreshInfrastructureLambda().trigger()
    return RenewInputPortForExplorationResponse(input_port_id=input_port.id)


@router.post("/{id}/input_ports/{output_port_id}/revoke")
def revoke_input_port_for_exploration(
    id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> RevokeInputPortForExplorationResponse:
    exp = ExplorationService(db).get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )

    input_port = ExplorationService(db).revoke_input_port(
        id, output_port_id, actor=authenticated_user
    )
    RefreshInfrastructureLambda().trigger()
    return RevokeInputPortForExplorationResponse(input_port_id=input_port.id)


@router.post("/{id}/input_ports/{output_port_id}/cancel")
def cancel_input_port_for_exploration(
    id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CancelInputPortForExplorationResponse:
    exploration_service = ExplorationService(db)
    exp = exploration_service.get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )
    input_port = exploration_service.cancel_input_port_request(
        id, output_port_id, actor=authenticated_user
    )
    RefreshInfrastructureLambda().trigger()
    return CancelInputPortForExplorationResponse(input_port_id=input_port.id)


@router.delete(
    "/{id}/input_ports/{output_port_id}",
)
def remove_input_port_for_exploration(
    id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    exploration_service = ExplorationService(db)
    exp = exploration_service.get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )
    exploration_service.remove_input_port(id, output_port_id)
    RefreshInfrastructureLambda().trigger()


@router.delete(
    "/{id}",
    responses={
        200: {"description": "Exploration deleted"},
        202: {"description": "Exploration marked for deletion, waiting for finalizers"},
        404: {
            "description": "Exploration not found",
            "content": {
                "application/json": {"example": {"detail": "Exploration id not found"}}
            },
        },
    },
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_EXPLORATION, EmptyResolver))
    ],
)
def remove_exploration(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    service = ExplorationService(db)
    exp = service.get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )
    can_delete = service.mark_for_deletion(id)
    if can_delete:
        service.remove_exploration(id)
    else:
        return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    "/{id}/finalizers",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_EXPLORATION, EmptyResolver))
    ],
)
def add_exploration_finalizer(
    id: UUID,
    request: FinalizerRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    exp = ExplorationService(db).get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )
    ExplorationService(db).add_finalizer(id, request.finalizer)


@router.delete(
    "/{id}/finalizers/{finalizer}",
    dependencies=[
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_EXPLORATION, EmptyResolver))
    ],
)
def remove_exploration_finalizer(
    id: UUID,
    finalizer: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    service = ExplorationService(db)
    exp = service.get_exploration(id, authenticated_user)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this exploration",
        )
    should_delete = service.remove_finalizer(id, finalizer)
    if should_delete:
        service.remove_exploration(id)
