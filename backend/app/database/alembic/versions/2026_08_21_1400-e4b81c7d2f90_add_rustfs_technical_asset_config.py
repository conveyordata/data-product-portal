"""Add RustFS technical asset configuration table

Revision ID: e4b81c7d2f90
Revises: 44b3eff9ab38
Create Date: 2026-08-21 14:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "e4b81c7d2f90"
down_revision: Union[str, None] = "44b3eff9ab38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rustfs_technical_asset_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("bucket", sa.String(), nullable=True),
        sa.Column("suffix", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("rustfs_technical_asset_configurations")
