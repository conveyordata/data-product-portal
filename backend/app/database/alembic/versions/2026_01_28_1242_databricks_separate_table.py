"""Migrate Databricks configurations to separate table

Revision ID: databricks_separate_table
Revises: snowflake_separate_table
Create Date: 2026-01-28 12:42:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "databricks_separate_table"
down_revision: Union[str, None] = "snowflake_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new databricks_technical_asset_configurations table
    op.create_table(
        "databricks_technical_asset_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("catalog", sa.String(), nullable=True),
        sa.Column("schema", sa.String(), nullable=True),
        sa.Column("bucket_identifier", sa.String(), nullable=True),
        sa.Column("catalog_path", sa.String(), nullable=True),
        sa.Column("table", sa.String(), nullable=True),
        sa.Column("table_path", sa.String(), nullable=True),
        sa.Column("access_granularity", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )

    # Migrate existing Databricks data
    op.execute(
        """
        INSERT INTO databricks_technical_asset_configurations
            (id, catalog, schema, bucket_identifier, catalog_path, "table", table_path, access_granularity, created_on, updated_on, deleted_at)
        SELECT
            id, catalog, schema, bucket_identifier, catalog_path, "table", table_path, access_granularity, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'DatabricksDataOutput'
        """
    )

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'DatabricksTechnicalAssetConfiguration'
        WHERE configuration_type = 'DatabricksDataOutput'
        """
    )

    # Remove Databricks-specific columns from base table to avoid duplicate data
    op.execute(
        """
        UPDATE data_output_configurations
        SET
            catalog = NULL,
            schema = NULL,
            bucket_identifier = NULL,
            catalog_path = NULL,
            "table" = NULL,
            table_path = NULL,
            access_granularity = NULL
        WHERE configuration_type = 'DatabricksTechnicalAssetConfiguration'
        """
    )


def downgrade() -> None:
    # Migrate all Databricks data back to base table (including newly created rows)
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'DatabricksDataOutput'
        WHERE configuration_type = 'DatabricksTechnicalAssetConfiguration'
        """
    )
    op.execute(
        """
        UPDATE data_output_configurations AS base
        SET
            catalog = db.catalog,
            schema = db.schema,
            bucket_identifier = db.bucket_identifier,
            catalog_path = db.catalog_path,
            "table" = db."table",
            table_path = db.table_path,
            access_granularity = db.access_granularity
        FROM databricks_technical_asset_configurations AS db
        WHERE base.id = db.id
        """
    )

    op.drop_table("databricks_technical_asset_configurations")
