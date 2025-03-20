from sqlalchemy.orm import Session

from .model import ThemeSettings as ThemeSettingsModel
from .schema import ThemeSettings as ThemeSettingsSchema


class ThemeSettingsService:

    def getThemeSettings(self, db: Session) -> ThemeSettingsSchema:
        return ThemeSettingsModel.getSettings(db)

    def updateThemeSettings(self, new_settings: ThemeSettingsSchema, db: Session):
        current_settings = ThemeSettingsModel.getSettings(db)
        updated_settings = new_settings.model_dump(exclude_unset=True)

        for attr, value in updated_settings.items():
            setattr(current_settings, attr, value)

        db.commit()
