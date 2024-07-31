"""Add unique key to env_platform_service_configs table

Revision ID: ab4a604ab521
Revises: 9dd3c640f180
Create Date: 2024-07-31 18:21:58.854830

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ab4a604ab521"
down_revision: Union[str, None] = "9dd3c640f180"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_env_platform_service",
        "env_platform_service_configs",
        ["environment_id", "platform_id", "service_id", "deleted_at"],
        postgresql_nulls_not_distinct=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_env_platform_service", "env_platform_service_configs", type_="unique"
    )
