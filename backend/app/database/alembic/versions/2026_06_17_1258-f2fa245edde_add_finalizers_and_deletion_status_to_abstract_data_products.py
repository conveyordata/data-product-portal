"""add finalizers and status to abstract_data_products

Revision ID: f2fa245edde
Revises: 8aa8df18d6ff
Create Date: 2026-06-17 12:58:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f2fa245edde"
down_revision: Union[str, None] = "8aa8df18d6ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add finalizers array
    op.add_column(
        "abstract_data_products",
        sa.Column(
            "finalizers",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
    )
    # Move status from data_products to abstract_data_products
    op.add_column(
        "abstract_data_products",
        sa.Column(
            "status",
            sa.String(),
            nullable=True,
        ),
    )
    # Copy existing status values from data_products to abstract_data_products
    op.execute(
        """
        UPDATE abstract_data_products adp
        SET status = dp.status
        FROM data_products dp
        WHERE dp.id = adp.id
        """
    )
    # Explorations get ACTIVE by default
    op.execute(
        """
        UPDATE abstract_data_products
        SET status = 'active'
        WHERE status IS NULL
        """
    )
    op.alter_column("abstract_data_products", "status", nullable=False)
    op.drop_column("data_products", "status")


def downgrade() -> None:
    op.add_column(
        "data_products",
        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="active",
        ),
    )
    op.execute(
        """
        UPDATE data_products dp
        SET status = adp.status
        FROM abstract_data_products adp
        WHERE adp.id = dp.id
        """
    )
    op.drop_column("abstract_data_products", "status")
    op.drop_column("abstract_data_products", "finalizers")
