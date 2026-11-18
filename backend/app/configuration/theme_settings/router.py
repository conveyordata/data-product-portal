from fastapi import APIRouter, Depends

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.deps import DbSession

from .schema_response import ThemeSettings
from .service import ThemeSettingsService

router = APIRouter(
    tags=["Configuration - Theme settings"], prefix="/v2/configuration/theme_settings"
)


@router.get("")
def get_theme_settings(
    db: DbSession,
) -> ThemeSettings:
    return ThemeSettingsService(db).get_theme_settings()


@router.put(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_theme_settings(
    new_settings: ThemeSettings,
    db: DbSession,
):
    return ThemeSettingsService(db).update_theme_settings(new_settings)
