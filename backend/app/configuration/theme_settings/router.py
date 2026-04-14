from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

from .schema_response import ThemeSettings
from .service import ThemeSettingsService

router = APIRouter(
    tags=["Configuration - Theme settings"], prefix="/v2/configuration/theme_settings"
)


@router.get("")
def get_theme_settings(db: Session = Depends(get_db_session)) -> ThemeSettings:
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
    new_settings: ThemeSettings, db: Session = Depends(get_db_session)
):
    return ThemeSettingsService(db).update_theme_settings(new_settings)
