from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.general_settings.schema import GeneralSettings
from app.general_settings.service import GeneralSettingsService

router = APIRouter(prefix="/general_settings", tags=["general_settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db_session)) -> GeneralSettings:
    return GeneralSettingsService().getGeneralSettings(db)


@router.put("")
def update_settings(
    new_settings: GeneralSettings, db: Session = Depends(get_db_session)
):
    return GeneralSettingsService().updateGeneralSettings(new_settings, db)
