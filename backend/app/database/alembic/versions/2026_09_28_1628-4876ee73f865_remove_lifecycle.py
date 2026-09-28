"""Remove lifecycle

Revision ID: 4876ee73f865
Revises: 18fb80f18c7d
Create Date: 2026-09-28 16:28:05.193862

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "4876ee73f865"
down_revision: Union[str, None] = "18fb80f18c7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("data_products_lifecycle_id_fkey", "data_products")
    op.drop_constraint("datasets_lifecycle_id_fkey", "datasets")
    op.drop_column("data_products", "lifecycle_id")
    op.drop_column("datasets", "lifecycle_id")
    op.drop_table("data_product_lifecycles")


def downgrade() -> None:
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
            sa.ForeignKey("data_product_lifecycles.id", ondelete="SET NULL"),
        ),
    )
    op.add_column(
        "datasets",
        sa.Column(
            "lifecycle_id",
            UUID,
            sa.ForeignKey("data_product_lifecycles.id", ondelete="SET NULL"),
        ),
    )
    op.execute(
        "INSERT INTO data_product_lifecycles (id, name, value, color, is_default) "
        "VALUES ('00000000-0000-0000-0000-000000000001', 'Draft', 0, 'grey', true)"
    )
