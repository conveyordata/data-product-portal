"""Add unique key to platform_service_configs table

Revision ID: 926e7e37f11e
Revises: ab4a604ab521
Create Date: 2024-08-02 14:23:58.039062

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "926e7e37f11e"
down_revision: Union[str, None] = "ab4a604ab521"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_platform_service",
        "platform_service_configs",
        ["platform_id", "service_id", "deleted_at"],
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_platform_service", "platform_service_configs", type_="unique"
    )
