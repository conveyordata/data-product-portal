from uuid import UUID

from sqlalchemy import Table, text  # noqa: TID251
from sqlalchemy.orm import Session

from app.database.visibility import acting_as as as_user

__all__ = ["as_user", "row_lock_modes"]


def row_lock_modes(session: Session, table: Table, id: UUID) -> set[str]:
    """The row locks held on a row, e.g. {"For Update"}, as seen by pgrowlocks."""
    return set(
        session.scalars(
            text(
                f"select unnest(locks.modes) from pgrowlocks('{table.name}') locks"  # noqa: S608
                f" join {table.name} on {table.name}.ctid = locks.locked_row"
                f" where {table.name}.id = :id"
            ),
            {"id": id},
        )
    )
