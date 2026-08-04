from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.configuration.access_modes.model import AccessMode
from app.configuration.access_modes.schema_request import (
    AccessModeCreate,
    AccessModeUpdate,
)
from app.database.database import get_db_session


class AccessModeService:
    def __init__(self, db: Session = Depends(get_db_session)) -> None:
        self.db = db

    def create_access_mode(self, access_mode: AccessModeCreate) -> "AccessMode":
        access_mode_model = AccessMode(**access_mode.parse_pydantic_schema())
        self.db.add(access_mode_model)
        self.db.flush()
        return access_mode_model

    def update_access_mode(
        self, id: UUID, update: AccessModeUpdate
    ) -> type[AccessMode]:
        access_mode = self.db.get(AccessMode, id)
        if not access_mode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Access mode {id} not found",
            )
        for key, value in update.parse_pydantic_schema().items():
            setattr(access_mode, key, value)
        self.db.flush()
        return access_mode

    def get_access_modes(self) -> list[type[AccessMode]]:
        return self.db.query(AccessMode).all()
