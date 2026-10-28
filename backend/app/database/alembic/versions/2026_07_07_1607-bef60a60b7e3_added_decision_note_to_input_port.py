"""Added decision note to input port

Revision ID: bef60a60b7e3
Revises: 56e4e97d7294
Create Date: 2026-07-07 16:07:40.773158

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bef60a60b7e3"
down_revision: Union[str, None] = "56e4e97d7294"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "input_ports",
        sa.Column("decision_note", sa.Text(), nullable=True),
    )
    op.execute(
        "UPDATE input_ports "
        "SET decision_note = 'N/A - added during migration' "
        "WHERE status = 'DENIED' AND decision_note IS NULL"
    )
    op.create_check_constraint(
        "ck_input_ports_decision_note_required_when_denied",
        "input_ports",
        "status != 'DENIED' OR decision_note IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_input_ports_decision_note_required_when_denied",
        "input_ports",
        type_="check",
    )
    op.drop_column("input_ports", "decision_note")
