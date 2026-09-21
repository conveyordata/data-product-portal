"""Migrate Databricks configurations to separate table

Revision ID: databricks_separate_table
Revises: snowflake_separate_table
Create Date: 2026-01-28 12:42:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "databricks_separate_table"
down_revision: Union[str, None] = "snowflake_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
# This migration reads columns off data_output_configurations that a later
# core migration removes, so it must run at this exact point in core's own
# history - it can't move into the plugin's independent branch. It only
# needs the databricks plugin's own baseline to have created the table first.
depends_on: Union[str, Sequence[str], None] = "databricks_0001_baseline"


def upgrade() -> None:
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

    op.drop_table("databricks_technical_asset_configurations", if_exists=True)
