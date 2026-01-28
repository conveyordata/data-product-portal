"""Migrate Redshift configurations to separate table

Revision ID: redshift_separate_table
Revises: glue_separate_table
Create Date: 2026-01-28 12:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "redshift_separate_table"
down_revision: Union[str, None] = "glue_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new redshift_data_output_configurations table
    op.create_table(
        "redshift_data_output_configurations",
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

    # Migrate existing Redshift data
    op.execute(
        """
        INSERT INTO redshift_data_output_configurations
            (id, database, schema, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at)
        SELECT
            id, database, schema, "table", bucket_identifier, database_path, table_path, access_granularity, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'RedshiftDataOutput'
        """
    )


def downgrade() -> None:
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
        FROM redshift_data_output_configurations AS rs
        WHERE base.id = rs.id
        """
    )

    op.drop_table("redshift_data_output_configurations")
