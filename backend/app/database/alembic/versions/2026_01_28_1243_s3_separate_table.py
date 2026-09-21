"""Migrate S3 configurations to separate table

Revision ID: s3_separate_table
Revises: databricks_separate_table
Create Date: 2026-01-28 12:43:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "s3_separate_table"
down_revision: Union[str, None] = "databricks_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
# This migration reads columns off data_output_configurations that a later
# core migration removes, so it must run at this exact point in core's own
# history - it can't move into the plugin's independent branch. It only
# needs the s3 plugin's own baseline to have created the table first.
depends_on: Union[str, Sequence[str], None] = "s3_0001_baseline"


def upgrade() -> None:
    # Migrate existing S3 data
    op.execute(
        """
        INSERT INTO s3_technical_asset_configurations
            (id, bucket, suffix, path, created_on, updated_on, deleted_at)
        SELECT
            id, bucket, suffix, path, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'S3DataOutput'
        """
    )

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'S3TechnicalAssetConfiguration'
        WHERE configuration_type = 'S3DataOutput'
        """
    )

    # Remove S3-specific columns from base table to avoid duplicate data
    op.execute(
        """
        UPDATE data_output_configurations
        SET
            bucket = NULL,
            suffix = NULL,
            path = NULL
        WHERE configuration_type = 'S3TechnicalAssetConfiguration'
        """
    )


def downgrade() -> None:
    # Migrate all S3 data back to base table (including newly created rows)
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'S3DataOutput'
        WHERE configuration_type = 'S3TechnicalAssetConfiguration'
        """
    )
    op.execute(
        """
        UPDATE data_output_configurations AS base
        SET
            bucket = s3.bucket,
            suffix = s3.suffix,
            path = s3.path
        FROM s3_technical_asset_configurations AS s3
        WHERE base.id = s3.id
        """
    )

    op.drop_table("s3_technical_asset_configurations", if_exists=True)
