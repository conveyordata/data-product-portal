from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "8b1e4f2c9a37"
down_revision: Union[str, None] = "3f9c2a7d1e04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "technical_asset_environment_overrides",
        sa.Column(
            "technical_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_outputs.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "environment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("environments.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("property", sa.String(), primary_key=True),
        sa.Column("value", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("technical_asset_environment_overrides")
