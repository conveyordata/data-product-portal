"""backfill invalid exploration access duration type

Migration 56e4e97d7294 backfilled every existing output port's
exploration_access_duration_type to "permanent", but 691b32ae42d8 only ever
seeded a "time_bound" access duration for explorations. Any output port
left on that default has no matching access_durations row, so requesting
it as an exploration input port always fails with a 500 (GH #4091).

Revision ID: c2a4e91f7b3d
Revises: 676a29542f0b
Create Date: 2026-09-03 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2a4e91f7b3d"
down_revision: Union[str, None] = "676a29542f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE datasets
        SET exploration_access_duration_type = ad.access_duration_type
        FROM access_durations ad
        WHERE ad.abstract_data_product_type = 'explorations'
          AND ad.is_default
          AND datasets.exploration_access_duration_type NOT IN (
              SELECT access_duration_type FROM access_durations
              WHERE abstract_data_product_type = 'explorations'
          )
        """
    )
    op.alter_column(
        "datasets",
        "exploration_access_duration_type",
        server_default="time_bound",
    )


def downgrade() -> None:
    op.alter_column(
        "datasets",
        "exploration_access_duration_type",
        server_default="permanent",
    )
