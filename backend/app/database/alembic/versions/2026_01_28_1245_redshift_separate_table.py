"""Migrate Redshift configurations to separate table

Revision ID: redshift_separate_table
Revises: glue_separate_table
Create Date: 2026-01-28 12:45:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "redshift_separate_table"
down_revision: Union[str, None] = "glue_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = "redshift_0001_baseline"


def upgrade() -> None:
    # No-op: every install already ran this in v0.5.0-0.7.3; older installs must upgrade to 0.7.3 first.
    pass


def downgrade() -> None:
    pass
