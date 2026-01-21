"""Add entire_schema checkbox

Revision ID: dbe6fbe45eef
Revises: 49990691cd30
Create Date: 2026-01-07 14:55:10.067397

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dbe6fbe45eef"
down_revision: Union[str, None] = "49990691cd30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_output_configurations",
        sa.Column(
            "access_granularity",
            sa.String,
            nullable=True,
        ),
    )
    # If not s3 data output, set access granularity to Schema if table_path is *, else Table
    op.execute(
        """
        UPDATE data_output_configurations
        SET access_granularity = CASE
            WHEN table_path = '*' THEN 'schema'
            ELSE 'table'
        END
        WHERE configuration_type != 'S3DataOutput';
    """
    )


def downgrade() -> None:
    op.drop_column("data_output_configurations", "access_granularity")
