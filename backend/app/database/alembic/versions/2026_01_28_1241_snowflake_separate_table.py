"""Migrate Snowflake configurations to separate table

Revision ID: snowflake_separate_table
Revises: 7601ac14662a
Create Date: 2026-01-28 12:41:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "snowflake_separate_table"
down_revision: Union[str, None] = "7601ac14662a"
branch_labels: Union[str, Sequence[str], None] = None
# This migration reads columns off data_output_configurations that a later
# core migration removes, so it must run at this exact point in core's own
# history - it can't move into the plugin's independent branch. It only
# needs the snowflake plugin's own baseline to have created the table first.
depends_on: Union[str, Sequence[str], None] = "snowflake_0001_baseline"


def upgrade() -> None:
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

    # Drop the separate table so a full downgrade-to-base sweep reaches this
    # point with core's shared base table no longer referenced by it.
    op.drop_table("snowflake_technical_asset_configurations", if_exists=True)
