from sqlalchemy.orm import Session

from app.general_settings.model import GeneralSettings as GeneralSettingsModel
from app.general_settings.schema import GeneralSettings as GeneralSettingsSchema


class GeneralSettingsService:

    def getGeneralSettings(self, db: Session) -> GeneralSettingsSchema:
        return GeneralSettingsModel.getSettings(db)

    def updateGeneralSettings(self, new_settings: GeneralSettingsSchema, db: Session):
        current_settings = GeneralSettingsModel.getSettings(db)
        updated_settings = new_settings.model_dump(exclude_unset=True)

        for attr, value in updated_settings.items():
            setattr(current_settings, attr, value)

        db.commit()
