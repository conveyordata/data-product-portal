"""Migrate S3 configurations to separate table

Revision ID: s3_separate_table
Revises: databricks_separate_table
Create Date: 2026-01-28 12:43:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "s3_separate_table"
down_revision: Union[str, None] = "databricks_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = "s3_0001_baseline"


def upgrade() -> None:
    # No-op: every install already ran this in v0.5.0-0.7.3; older installs must upgrade to 0.7.3 first.
    pass


def downgrade() -> None:
    pass
