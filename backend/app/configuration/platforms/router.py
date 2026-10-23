from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.configuration.platforms.schema_response import (
    GetAllPlatformsResponse,
    PlatformEnvironmentSettings,
)
from app.configuration.platforms.service import PlatformSettingsService
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import get_db_session

router = APIRouter(
    tags=["Configuration - Platforms"], prefix="/v2/configuration/platforms"
)


@router.get("")
def get_all_platforms(
    db: Session = Depends(get_db_session, scope="function"),
) -> GetAllPlatformsResponse:
    return GetAllPlatformsResponse(
        platforms=PlatformSettingsService(db).get_platforms()
    )


@router.get(
    "/{platform_key}/environments/{environment_id}/settings",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def get_platform_environment_settings(
    platform_key: str,
    environment_id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> PlatformEnvironmentSettings:
    return PlatformSettingsService(db).get_settings(platform_key, environment_id)


@router.put(
    "/{platform_key}/environments/{environment_id}/settings",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_platform_environment_settings(
    platform_key: str,
    environment_id: UUID,
    settings: dict[str, Any] = Body(...),
    db: Session = Depends(get_db_session, scope="function"),
) -> PlatformEnvironmentSettings:
    return PlatformSettingsService(db).update_settings(
        platform_key, environment_id, settings
    )
