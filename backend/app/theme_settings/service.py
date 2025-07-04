from sqlalchemy.orm import Session

from .model import ThemeSettings as ThemeSettingsModel
from .schema import ThemeSettings as ThemeSettingsSchema


class ThemeSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_theme_settings(self) -> ThemeSettingsSchema:
        return ThemeSettingsModel.get_settings(self.db)

    def update_theme_settings(self, new_settings: ThemeSettingsSchema):
        current_settings = ThemeSettingsModel.get_settings(self.db)
        updated_settings = new_settings.model_dump(exclude_unset=True)

        for attr, value in updated_settings.items():
            setattr(current_settings, attr, value)

        self.db.commit()
