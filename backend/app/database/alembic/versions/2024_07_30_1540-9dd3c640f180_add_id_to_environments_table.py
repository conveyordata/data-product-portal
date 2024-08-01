"""Add ID to environments table

Revision ID: 9dd3c640f180
Revises: 45016ec9a7b7
Create Date: 2024-07-30 15:40:58.183952

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "9dd3c640f180"
down_revision: Union[str, None] = "45016ec9a7b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("permissionsets")
    op.drop_column("env_platform_service_configs", "environment")
    op.drop_constraint("environments_pkey", "environments", type_="primary")

    op.add_column(
        "environments",
        sa.Column("id", sa.UUID, server_default=sa.text("gen_random_uuid()")),
    )
    op.create_primary_key("environments_pkey", "environments", ["id"])
    op.create_unique_constraint("uq_environments_name", "environments", ["name"])
    op.add_column(
        "env_platform_service_configs",
        sa.Column("environment_id", sa.UUID, sa.ForeignKey("environments.id")),
    )


def downgrade() -> None:
    op.drop_column("env_platform_service_configs", "environment_id")
    op.drop_column("environments", "id")
    op.drop_constraint("uq_environments_name", "environments", type_="unique")

    op.create_primary_key("environments_pkey", "environments", ["name"])
    op.add_column(
        "env_platform_service_configs",
        sa.Column("environment", sa.String, sa.ForeignKey("environments.name")),
    )
    op.create_table(
        "permissionsets",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("data_product", sa.UUID, sa.ForeignKey("data_products.id")),
        sa.Column("environment", sa.String, sa.ForeignKey("environments.name")),
        sa.Column("name", sa.String),
        sa.Column("rolearn", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
