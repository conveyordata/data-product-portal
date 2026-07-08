"""add renewed by to input port

Revision ID: c7cd7b905f3e
Revises: f05841f3040e
Create Date: 2026-07-08 13:51:49.585693

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7cd7b905f3e"
down_revision: Union[str, None] = "f05841f3040e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "input_ports",
        sa.Column("renewed_by_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_input_ports_renewed_by_id_users",
        "input_ports",
        "users",
        ["renewed_by_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_input_ports_renewed_by_id_users",
        "input_ports",
        type_="foreignkey",
    )
    op.drop_column("input_ports", "renewed_by_id")
