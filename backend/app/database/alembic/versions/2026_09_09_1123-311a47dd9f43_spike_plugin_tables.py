"""spike_plugin_tables

Revision ID: 311a47dd9f43
Revises: ad035abcf21d
Create Date: 2026-09-09 11:23:14.653027

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "311a47dd9f43"
down_revision: Union[str, None] = "ad035abcf21d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ADR-0024 spike: one shared JSONB config column per plugin type,
    # instead of a dedicated table per type.
    op.create_table(
        "spike_technical_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "data_product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("plugin_key", sa.String(), nullable=False),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )

    # ADR-0024 spike: one shared JSONB config record per (plugin, environment),
    # instead of platforms/platform_services/env_platform_configs/env_platform_service_configs.
    op.create_table(
        "spike_environment_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plugin_key", sa.String(), nullable=False),
        sa.Column(
            "environment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("environments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )


def downgrade() -> None:
    op.drop_table("spike_environment_configs")
    op.drop_table("spike_technical_assets")
