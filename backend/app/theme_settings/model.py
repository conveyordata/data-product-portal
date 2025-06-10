from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from app.database.database import Base

SETTINGS_ID = 1


class ThemeSettings(Base):
    __tablename__ = "theme_settings"
    id = Column(Integer, primary_key=True, default=SETTINGS_ID)
    portal_name = Column(String)

    @staticmethod
    def get_settings(db: Session):
        return db.get(ThemeSettings, SETTINGS_ID)
