"""Add entire_schema checkbox

Revision ID: dbe6fbe45eef
Revises: ca5f5782790a
Create Date: 2026-01-07 14:55:10.067397

"""

from enum import UNIQUE, StrEnum, verify
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dbe6fbe45eef"
down_revision: Union[str, None] = "ca5f5782790a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


@verify(UNIQUE)
class AccessGranularity(StrEnum):
    Schema = "schema"
    Table = "table"


def upgrade() -> None:
    op.execute(
        """
        CREATE TYPE accessgranularity AS ENUM (
            'Schema',
            'Table'
        );
    """
    )
    op.add_column(
        "data_output_configurations",
        sa.Column(
            "access_granularity",
            sa.Enum(AccessGranularity),
            nullable=True,
        ),
    )
    # If not s3 data output, set access granularity to Schema if table_path is *, else Table
    op.execute(
        """
        UPDATE data_output_configurations
        SET access_granularity = CASE
            WHEN table_path = '*' THEN 'Schema'::accessgranularity
            ELSE 'Table'::accessgranularity
        END
        WHERE configuration_type != 'S3DataOutput';
    """
    )


def downgrade() -> None:
    op.drop_column("data_output_configurations", "access_granularity")
    op.execute("DROP TYPE accessgranularity;")
