from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session

from .schema import ThemeSettings
from .service import ThemeSettingsService

router = APIRouter(prefix="/theme_settings", tags=["theme_settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db_session)) -> ThemeSettings:
    return ThemeSettingsService(db).get_theme_settings()


@router.put(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__UPDATE_CONFIGURATION, EmptyResolver)
        ),
    ],
)
def update_settings(new_settings: ThemeSettings, db: Session = Depends(get_db_session)):
    return ThemeSettingsService(db).update_theme_settings(new_settings)
