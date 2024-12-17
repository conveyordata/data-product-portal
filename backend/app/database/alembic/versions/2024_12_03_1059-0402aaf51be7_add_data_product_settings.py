"""add data product settings

Revision ID: 0402aaf51be7
Revises: 3d6be1e9b5fa
Create Date: 2024-12-03 10:59:39.979406

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "0402aaf51be7"
down_revision: Union[str, None] = "3d6be1e9b5fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_product_settings",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("name", sa.String),
        sa.Column("external_id", sa.String),
        sa.Column("tooltip", sa.String),
        sa.Column("type", sa.String),
        sa.Column("divider", sa.String),
        sa.Column("default", sa.String),
        sa.Column("order", sa.Integer),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "data_products_settings_values",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column(
            "data_product_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("data_products.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "data_product_setting_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("data_product_settings.id", ondelete="CASCADE"),
        ),
        sa.Column("value", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("data_products_settings_values")
    op.drop_table("data_product_settings")
