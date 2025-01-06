"""add data product lifecycles

Revision ID: df605bd8b0a0
Revises: 3d6be1e9b5fa
Create Date: 2024-12-17 09:54:50.828048

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "df605bd8b0a0"
down_revision: Union[str, None] = "3d6be1e9b5fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_product_lifecycles",
        sa.Column("id", UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("color", sa.String(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=True, server_default="false"),
        sa.PrimaryKeyConstraint("id"),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.add_column(
        "data_products",
        sa.Column(
            "lifecycle_id",
            UUID,
            sa.ForeignKey("data_product_lifecycles.id"),
        ),
    )


def downgrade() -> None:
    op.drop_table("data_product_lifecycles")
    op.drop_column("data_products", "lifecycle_id")
