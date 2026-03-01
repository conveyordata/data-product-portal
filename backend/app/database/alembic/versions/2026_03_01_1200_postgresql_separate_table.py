"""Migrate PostgreSQL configurations to separate table

Revision ID: postgresql_separate_table
Revises: 638303a2cb77
Create Date: 2026-03-01 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "postgresql_separate_table"
down_revision: Union[str, None] = "638303a2cb77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new postgresql_technical_asset_configurations table
    op.create_table(
        "postgresql_technical_asset_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("database", sa.String(), nullable=True),
        sa.Column("schema", sa.String(), nullable=True),
        sa.Column("table", sa.String(), nullable=True),
        sa.Column("bucket_identifier", sa.String(), nullable=True),
        sa.Column("database_path", sa.String(), nullable=True),
        sa.Column("table_path", sa.String(), nullable=True),
        sa.Column("access_granularity", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )

    # Note: We assume there's no legacy data to migrate from data_output_configurations
    # as the postgresql configuration is newly introduced and wasn't present when the
    # other configurations were mixed in the same table.
    # If there was, we would insert it here and update the type.

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'PostgreSQLTechnicalAssetConfiguration'
        WHERE configuration_type = 'PostgreSQLDataOutput'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'PostgreSQLDataOutput'
        WHERE configuration_type = 'PostgreSQLTechnicalAssetConfiguration'
        """
    )

    op.drop_table("postgresql_technical_asset_configurations")
