"""add cascade delete to dataset_query_stats_daily

Revision ID: ca5f5782790a
Revises: 49990691cd30
Create Date: 2026-01-14 12:50:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ca5f5782790a"
down_revision: Union[str, None] = "49990691cd30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the old foreign key constraint
    op.drop_constraint(
        "dataset_query_stats_daily_dataset_id_fkey",
        "dataset_query_stats_daily",
        type_="foreignkey",
    )

    # Create the new foreign key constraint with ON DELETE CASCADE
    op.create_foreign_key(
        "dataset_query_stats_daily_dataset_id_fkey",
        "dataset_query_stats_daily",
        "datasets",
        ["dataset_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # Drop the cascade foreign key constraint
    op.drop_constraint(
        "dataset_query_stats_daily_dataset_id_fkey",
        "dataset_query_stats_daily",
        type_="foreignkey",
    )

    # Re-create the original foreign key constraint without ON DELETE CASCADE
    op.create_foreign_key(
        "dataset_query_stats_daily_dataset_id_fkey",
        "dataset_query_stats_daily",
        "datasets",
        ["dataset_id"],
        ["id"],
    )
