"""Data product visibility

Revision ID: 676a29542f0b
Revises: e4b81c7d2f90
Create Date: 2026-08-25 11:36:05.162137

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "676a29542f0b"
down_revision: Union[str, None] = "e4b81c7d2f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_products",
        sa.Column(
            "visibility",
            sa.String(),
            nullable=False,
            server_default="discoverable",
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE roles
            SET permissions = COALESCE(permissions, ARRAY[]::int[]) || :read_action
            WHERE scope = :scope
              AND NOT (:read_action = ANY(COALESCE(permissions, ARRAY[]::int[])))
            """
        ).bindparams(
            read_action=int(901),  # HIDDEN__DATA_PRODUCT__READ
            scope="data_product",  # Scope.DATA_PRODUCT
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE roles
            SET permissions = array_remove(permissions, :read_action)
            WHERE scope = :scope
            """
        ).bindparams(
            read_action=int(901),  # HIDDEN__DATA_PRODUCT__READ
            scope="data_product",  # Scope.DATA_PRODUCT
        )
    )
    op.drop_column("data_products", "visibility")
