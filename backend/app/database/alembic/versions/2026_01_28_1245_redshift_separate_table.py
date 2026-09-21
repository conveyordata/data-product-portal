"""Migrate Redshift configurations to separate table

Revision ID: redshift_separate_table
Revises: glue_separate_table
Create Date: 2026-01-28 12:45:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "redshift_separate_table"
down_revision: Union[str, None] = "glue_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
# This migration reads columns off data_output_configurations that a later
# core migration removes, so it must run at this exact point in core's own
# history - it can't move into the plugin's independent branch. It only
# needs the redshift plugin's own baseline to have created the table first.
depends_on: Union[str, Sequence[str], None] = "redshift_0001_baseline"


def upgrade() -> None:
    # Migrate existing Redshift data
    op.execute(
        """
        INSERT INTO redshift_technical_asset_configurations
            (id, database, schema, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at)
        SELECT
            id, database, schema, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'RedshiftDataOutput'
        """
    )

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'RedshiftTechnicalAssetConfiguration'
        WHERE configuration_type = 'RedshiftDataOutput'
        """
    )

    # Remove Redshift-specific columns from base table to avoid duplicate data
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
        WHERE configuration_type = 'RedshiftTechnicalAssetConfiguration'
        """
    )


def downgrade() -> None:
    # Migrate all Redshift data back to base table (including newly created rows)
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'RedshiftDataOutput'
        WHERE configuration_type = 'RedshiftTechnicalAssetConfiguration'
        """
    )
    op.execute(
        """
        UPDATE data_output_configurations AS base
        SET
            database = rs.database,
            schema = rs.schema,
            "table" = rs."table",
            bucket_identifier = rs.bucket_identifier,
            database_path = rs.database_path,
            table_path = rs.table_path,
            access_granularity = rs.access_granularity
        FROM redshift_technical_asset_configurations AS rs
        WHERE base.id = rs.id
        """
    )

    op.drop_table("redshift_technical_asset_configurations", if_exists=True)
