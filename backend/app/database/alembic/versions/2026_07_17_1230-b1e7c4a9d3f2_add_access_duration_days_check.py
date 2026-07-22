"""Add check constraint on access_duration days

Enforces the same invariant the API already validates: time-bound durations
must have a days value, permanent durations must not.

Revision ID: b1e7c4a9d3f2
Revises: aa9f983049d2
Create Date: 2026-07-17 12:30:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1e7c4a9d3f2"
down_revision: Union[str, None] = "aa9f983049d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_access_durations_days_matches_type",
        "access_durations",
        "(access_duration_type = 'time_bound' AND days IS NOT NULL) "
        "OR (access_duration_type = 'permanent' AND days IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_access_durations_days_matches_type",
        "access_durations",
        type_="check",
    )
