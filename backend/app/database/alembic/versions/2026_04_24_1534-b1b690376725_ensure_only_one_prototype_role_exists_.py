"""Ensure only one prototype role exists per scope

Revision ID: b1b690376725
Revises: 6449af439bdd
Create Date: 2026-04-24 15:34:54.005335

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1b690376725"
down_revision: Union[str, None] = "6449af439bdd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.create_index(
            "uq_roles_prototype_scope",
            "roles",
            ["prototype", "scope"],
            unique=True,
            postgresql_where=sa.text("prototype != 0"),
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index(
            "uq_roles_prototype_scope",
            table_name="roles",
            postgresql_concurrently=True,
        )
