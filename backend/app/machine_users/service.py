from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.machine_users.model import MachineUser, ensure_machine_user_exists
from app.machine_users.schema_request import MachineUserCreate, MachineUserUpdate
from app.machine_users.schema_response import (
    MachineUserCreateResponse,
    MachineUserGet,
    MachineUserUpdateResponse,
)


class MachineUserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_machine_users(self) -> Sequence[MachineUserGet]:
        return self.db.scalars(
            select(MachineUser).order_by(
                asc(MachineUser.display_name),
                asc(MachineUser.external_id),
            )
        ).all()

    def get_machine_user(self, machine_user_id: UUID) -> MachineUserGet:
        return ensure_machine_user_exists(machine_user_id, self.db)

    def create_machine_user(
        self,
        machine_user: MachineUserCreate,
    ) -> MachineUserCreateResponse:
        self._ensure_external_id_available(machine_user.external_id)

        machine_user_model = MachineUser(
            **machine_user.parse_pydantic_schema(),
        )
        self.db.add(machine_user_model)
        self.db.flush()

        return MachineUserCreateResponse(id=machine_user_model.id)

    def update_machine_user(
        self,
        machine_user_id: UUID,
        machine_user: MachineUserUpdate,
    ) -> MachineUserUpdateResponse:
        current_machine_user = ensure_machine_user_exists(
            machine_user_id,
            self.db,
        )

        current_machine_user.display_name = machine_user.display_name
        self.db.flush()

        return MachineUserUpdateResponse(id=current_machine_user.id)

    def delete_machine_user(self, machine_user_id: UUID) -> None:
        machine_user = ensure_machine_user_exists(machine_user_id, self.db)
        self.db.delete(machine_user)
        self.db.flush()

    def _ensure_external_id_available(self, external_id: str) -> None:
        existing_id = self.db.scalar(
            select(MachineUser.id).where(
                MachineUser.external_id == external_id,
            )
        )
        if existing_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A machine user with this external ID already exists.",
            )
