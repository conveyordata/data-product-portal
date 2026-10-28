from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.identities.schema_response import (
    IdentityBatchCreateError,
    IdentityBatchCreateResponse,
)
from app.identities.service import validate_batch_create_items
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
        self.authorizer = Authorization()

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

    def create_machine_users_batch(
        self,
        items: list[Any],
    ) -> IdentityBatchCreateResponse:
        validated_machine_users, errors = validate_batch_create_items(
            items,
            MachineUserCreate,
        )

        external_ids = {
            machine_user.external_id for machine_user in validated_machine_users
        }

        unavailable_external_ids: set[str] = (
            set(
                self.db.scalars(
                    select(MachineUser.external_id).where(
                        MachineUser.external_id.in_(external_ids)
                    )
                ).all()
            )
            if external_ids
            else set()
        )

        machine_users: list[MachineUser] = []
        for machine_user in validated_machine_users:
            if machine_user.external_id in unavailable_external_ids:
                errors.append(
                    IdentityBatchCreateError(
                        item=machine_user,
                        errors=["A machine user with this external ID already exists."],
                    )
                )
                continue

            # Reserve the ID so later duplicates in this request are rejected.
            unavailable_external_ids.add(machine_user.external_id)
            machine_users.append(MachineUser(**machine_user.parse_pydantic_schema()))

        self.db.add_all(machine_users)
        self.db.flush()

        return IdentityBatchCreateResponse(
            ids=[machine_user.id for machine_user in machine_users],
            errors=errors,
        )

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
        self.authorizer.clear_assignments_for_user(user_id=machine_user.id)
        self.db.delete(machine_user)
        self.db.flush()

    def delete_machine_users_batch(self, ids: list[UUID]) -> None:
        """Marks for deletion all machine users with the given ids"""
        machine_users = self.db.scalars(
            select(MachineUser).where(MachineUser.id.in_(ids))
        ).all()

        self.authorizer.clear_assignments_for_identities(
            identity_ids=[machine_user.id for machine_user in machine_users],
        )

        for machine_user in machine_users:
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
