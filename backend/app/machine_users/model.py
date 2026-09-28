import uuid
from typing import Any, Sequence

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, Session

from app.database.database import ensure_exists
from app.identities.model import Identity
from app.identities.type import IdentityType


class MachineUser(Identity):
    __tablename__ = "machine_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": IdentityType.MACHINE_USER.value,
    }

def ensure_machine_user_exists(
    machine_user_id: uuid.UUID,
    db: Session,
    options: Sequence[Any] = (),
) -> MachineUser:
    return ensure_exists(machine_user_id, db, MachineUser, options=options)