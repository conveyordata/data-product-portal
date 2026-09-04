"""domain environments

Revision ID: 6271ee228708
Revises: 676a29542f0b
Create Date: 2026-09-01 11:14:16.229781

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "6271ee228708"
down_revision: Union[str, None] = "676a29542f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_environments",
        sa.Column(
            "domain_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("domains.id"),
            nullable=False,
            primary_key=True,
            index=True,
        ),
        sa.Column(
            "environment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("environments.id"),
            nullable=False,
            primary_key=True,
            index=True,
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.add_column(
        "environments",
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table("domain_environments")
    op.drop_column("environments", "is_global")
