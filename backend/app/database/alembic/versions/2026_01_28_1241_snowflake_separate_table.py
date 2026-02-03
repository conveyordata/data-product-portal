"""Migrate Snowflake configurations to separate table

Revision ID: snowflake_separate_table
Revises: 7601ac14662a
Create Date: 2026-01-28 12:41:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "snowflake_separate_table"
down_revision: Union[str, None] = "7601ac14662a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new snowflake_technical_asset_configurations table
    # The 'id' column is both a primary key and a foreign key to data_output_configurations
    op.create_table(
        "snowflake_technical_asset_configurations",
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

    # Migrate existing Snowflake data from polymorphic table to new table
    # Note: The base table data_output_configurations already has the id and timestamps,
    # we just need to copy the Snowflake-specific columns
    op.execute(
        """
        INSERT INTO snowflake_technical_asset_configurations
            (id, database, schema, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at)
        SELECT
            id, database, schema, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'SnowflakeDataOutput'
        """
    )

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'SnowflakeTechnicalAssetConfiguration'
        WHERE configuration_type = 'SnowflakeDataOutput'
        """
    )

    # Remove Snowflake-specific columns from base table to avoid duplicate data
    op.execute(
        """
        UPDATE data_output_configurations
        SET
            database = NULL,
            schema = NULL,
            "table" = NULL,
            bucket_identifier = NULL,
            database_path = NULL,
            table_path = NULL,
            access_granularity = NULL
        WHERE configuration_type = 'SnowflakeTechnicalAssetConfiguration'
        """
    )


def downgrade() -> None:
    # Migrate all Snowflake data back to base table (including newly created rows)
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'SnowflakeDataOutput'
        WHERE configuration_type = 'SnowflakeTechnicalAssetConfiguration'
        """
    )
    op.execute(
        """
        UPDATE data_output_configurations AS base
        SET
            database = sf.database,
            schema = sf.schema,
            "table" = sf."table",
            bucket_identifier = sf.bucket_identifier,
            database_path = sf.database_path,
            table_path = sf.table_path,
            access_granularity = sf.access_granularity
        FROM snowflake_technical_asset_configurations AS sf
        WHERE base.id = sf.id
        """
    )

    # Drop the separate table
    op.drop_table("snowflake_technical_asset_configurations")
