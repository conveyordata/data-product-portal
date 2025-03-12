"""add extra databricks and snowflake configuration options

Revision ID: 6516756ada04
Revises: 3d6be1e9b5fa
Create Date: 2024-11-21 15:20:45.565430

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6516756ada04"
down_revision: Union[str, None] = "3d6be1e9b5fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """UPDATE "data_output_configurations" set "table" = '*'
        where configuration_type IN ('DatabricksDataOutput',
          'SnowflakeDataOutput') and "table" is null"""
    )
    op.execute(
        """UPDATE "data_output_configurations" set table_path = ''
        where configuration_type IN ('DatabricksDataOutput',
        'SnowflakeDataOutput') and table_path is null"""
    )
    op.execute(
        """UPDATE "data_output_configurations" set
          bucket_identifier = '' where configuration_type IN
          ('DatabricksDataOutput', 'SnowflakeDataOutput')
          and bucket_identifier is null"""
    )
    op.execute(
        """UPDATE "data_output_configurations" set
          schema_path = '' where configuration_type IN
          ('DatabricksDataOutput', 'SnowflakeDataOutput') and schema_path is null"""
    )


def downgrade() -> None:
    pass
