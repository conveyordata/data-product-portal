"""drop configurations

Revision ID: 2bac081ab9d0
Revises: redshift_separate_table
Create Date: 2026-01-28 13:33:52.105527

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2bac081ab9d0"
down_revision: Union[str, None] = "redshift_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop all but id and configuration_type columns from data_output_configurations
    with op.batch_alter_table("data_output_configurations") as batch_op:
        batch_op.drop_column("bucket")
        batch_op.drop_column("suffix")
        batch_op.drop_column("path")
        batch_op.drop_column("catalog")
        batch_op.drop_column("database")
        batch_op.drop_column("database_suffix")
        batch_op.drop_column("table")
        batch_op.drop_column("bucket_identifier")
        batch_op.drop_column("database_path")
        batch_op.drop_column("table_path")
        batch_op.drop_column("access_granularity")
        batch_op.drop_column("schema")
        batch_op.drop_column("schema_suffix")
        batch_op.drop_column("catalog_path")
        batch_op.drop_column("schema_path")


def downgrade() -> None:
    # Re-add dropped columns to data_output_configurations
    with op.batch_alter_table("data_output_configurations") as batch_op:
        batch_op.add_column(sa.Column("schema", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("access_granularity", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("table_path", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("database_path", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("bucket_identifier", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("table", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("database_suffix", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("database", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("catalog", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("path", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("suffix", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("bucket", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("schema_suffix", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("catalog_path", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("schema_path", sa.String(), nullable=True))
