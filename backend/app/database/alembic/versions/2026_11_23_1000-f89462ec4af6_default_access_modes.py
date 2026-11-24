"""Default access mode per technical asset type

Revision ID: f89462ec4af6
Revises: 8a1d4c7e2f90
Create Date: 2026-11-23 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "f89462ec4af6"
down_revision: Union[str, None] = "8a1d4c7e2f90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "default_access_modes",
        sa.Column("technical_asset_type", sa.Text(), primary_key=True),
        sa.Column(
            "access_mode_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("access_modes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.execute(
        """
        INSERT INTO default_access_modes (technical_asset_type, access_mode_id)
        SELECT DISTINCT ON (technical_asset_type) technical_asset_type, access_modes.id
        FROM access_modes,
            unnest(access_modes.technical_asset_types) AS technical_asset_type
        ORDER BY technical_asset_type, access_modes.created_on, access_modes.name
        """
    )


def downgrade() -> None:
    op.drop_table("default_access_modes")
