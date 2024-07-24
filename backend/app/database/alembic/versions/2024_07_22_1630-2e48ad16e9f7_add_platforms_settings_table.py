"""Add platforms_settings table

Revision ID: 2e48ad16e9f7
Revises: 4e61079eaf16
Create Date: 2024-07-22 16:30:53.496277

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.environments.enums import PlatformTypes
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "2e48ad16e9f7"
down_revision: Union[str, None] = "4e61079eaf16"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platforms",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column("name", sa.Enum(PlatformTypes)),
        sa.Column("settings", sa.String),
        sa.Column("environment", sa.String, sa.ForeignKey("environments.name")),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_unique_constraint(
        "uq_env_platform_deleted_at", "platforms", ["environment", "name", "deleted_at"]
    )

    op.drop_column("environments", "context")


def downgrade() -> None:
    op.drop_table("platforms")
    op.execute("DROP TYPE platformtypes;")

    op.add_column("environments", sa.Column("context", sa.String))
