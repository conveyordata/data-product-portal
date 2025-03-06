from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin

from .schema import ThemeSettings
from .service import ThemeSettingsService

router = APIRouter(prefix="/theme_settings", tags=["theme_settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db_session)) -> ThemeSettings:
    return ThemeSettingsService().getThemeSettings(db)


@router.put("", dependencies=[Depends(only_for_admin)])
def update_settings(new_settings: ThemeSettings, db: Session = Depends(get_db_session)):
    return ThemeSettingsService().updateThemeSettings(new_settings, db)
