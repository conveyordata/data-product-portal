"""Migrate Glue configurations to separate table

Revision ID: glue_separate_table
Revises: s3_separate_table
Create Date: 2026-01-28 12:44:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "glue_separate_table"
down_revision: Union[str, None] = "s3_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
# This migration reads columns off data_output_configurations that a later
# core migration removes, so it must run at this exact point in core's own
# history - it can't move into the plugin's independent branch. It only
# needs the glue plugin's own baseline to have created the table first.
depends_on: Union[str, Sequence[str], None] = "glue_0001_baseline"


def upgrade() -> None:
    # Migrate existing Glue data
    op.execute(
        """
        INSERT INTO glue_technical_asset_configurations
            (id, database, database_suffix, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at)
        SELECT
            id, database, database_suffix, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'GlueDataOutput'
        """
    )

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'GlueTechnicalAssetConfiguration'
        WHERE configuration_type = 'GlueDataOutput'
        """
    )

    # Remove Glue-specific columns from base table to avoid duplicate data
    op.execute(
        """
        UPDATE data_output_configurations
        SET
            database = NULL,
            database_suffix = NULL,
            "table" = NULL,
            bucket_identifier = NULL,
            database_path = NULL,
            table_path = NULL,
            access_granularity = NULL
        WHERE configuration_type = 'GlueTechnicalAssetConfiguration'
        """
    )


def downgrade() -> None:
    # Migrate all Glue data back to base table (including newly created rows)
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'GlueDataOutput'
        WHERE configuration_type = 'GlueTechnicalAssetConfiguration'
        """
    )
    op.execute(
        """
        UPDATE data_output_configurations AS base
        SET
            database = glue.database,
            database_suffix = glue.database_suffix,
            "table" = glue."table",
            bucket_identifier = glue.bucket_identifier,
            database_path = glue.database_path,
            table_path = glue.table_path,
            access_granularity = glue.access_granularity
        FROM glue_technical_asset_configurations AS glue
        WHERE base.id = glue.id
        """
    )

    op.drop_table("glue_technical_asset_configurations", if_exists=True)
