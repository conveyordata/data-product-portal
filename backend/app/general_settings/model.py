from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from app.database.database import Base

SETTINGS_ID = 1


class GeneralSettings(Base):
    __tablename__ = "general_settings"
    id = Column(Integer, primary_key=True, default=SETTINGS_ID)
    portal_name = Column(String)

    @staticmethod
    def getSettings(db: Session):
        return db.get(GeneralSettings, SETTINGS_ID)
