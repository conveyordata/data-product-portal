from uuid import UUID

from fastapi import APIRouter, Depends

from app.configuration.access_modes.schema_request import (
    AccessModeCreate,
    AccessModeUpdate,
)
from app.configuration.access_modes.schema_response import (
    AccessMode,
    AccessModeWithType,
    GetAccessModes,
)
from app.configuration.access_modes.service import (
    ACCESS_MODE_NOT_FOUND_ERROR,
    CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR,
    CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR,
    AccessModeService,
)
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.core.errors.router_responses import process_errors_as_route_responses

router = APIRouter(
    tags=["Configuration - Access Modes"],
    prefix="/v2/configuration/access_modes",
)


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def create_access_mode(
    access_mode: AccessModeCreate,
    access_mode_service: AccessModeService = Depends(AccessModeService),
) -> AccessMode:
    return AccessMode.model_validate(
        access_mode_service.create_access_mode(access_mode)
    )


@router.put(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_access_mode(
    id: UUID,
    update: AccessModeUpdate,
    access_mode_service: AccessModeService = Depends(AccessModeService),
) -> AccessMode:
    return AccessMode.model_validate(access_mode_service.update_access_mode(id, update))


@router.get(
    "",
    responses=process_errors_as_route_responses(
        [
            CAN_NOT_REMOVE_TECHNICAL_ASSET_TYPES_ERROR,
            ACCESS_MODE_NOT_FOUND_ERROR,
        ]
    ),
)
def get_access_modes(
    access_mode_service: AccessModeService = Depends(AccessModeService),
) -> GetAccessModes:
    return GetAccessModes(
        access_modes=[
            AccessModeWithType.model_validate(am)
            for am in access_mode_service.get_access_modes()
        ],
    )


@router.delete(
    "/{id}",
    responses=process_errors_as_route_responses(
        [
            CAN_NOT_REMOVE_ACCESS_MODE_IN_USE_ERROR,
        ]
    ),
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def delete_access_mode(
    id: UUID,
    access_mode_service: AccessModeService = Depends(AccessModeService),
) -> None:
    access_mode_service.delete_access_mode(id)
