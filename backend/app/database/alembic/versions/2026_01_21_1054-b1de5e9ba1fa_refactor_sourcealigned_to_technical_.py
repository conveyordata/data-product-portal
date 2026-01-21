"""Refactor sourceAligned to Technical Mapping

Revision ID: b1de5e9ba1fa
Revises: dbe6fbe45eef
Create Date: 2026-01-21 10:54:04.011858

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1de5e9ba1fa"
down_revision: Union[str, None] = "dbe6fbe45eef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_outputs", sa.Column("technical_mapping", sa.String, nullable=True)
    )
    op.execute(
        """
        UPDATE data_outputs
        SET technical_mapping = CASE
            WHEN "sourceAligned" = TRUE THEN 'custom'
            ELSE 'default'
        END
        """
    )
    op.alter_column("data_outputs", "technical_mapping", nullable=False)
    op.drop_column("data_outputs", "sourceAligned")


def downgrade() -> None:
    op.add_column("data_outputs", sa.Column("sourceAligned", sa.Boolean, nullable=True))
    op.execute(
        """
        UPDATE data_outputs
        SET "sourceAligned" = CASE
            WHEN technical_mapping = 'custom' THEN TRUE
            ELSE FALSE
        END
        """
    )
    op.alter_column("data_outputs", "sourceAligned", nullable=False)
    op.drop_column("data_outputs", "technical_mapping")
