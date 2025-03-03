"""add roles table

Revision ID: 2a58b7ce3cea
Revises: d98efbda5e7c
Create Date: 2025-02-27 13:22:30.955690

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.authz.actions import AuthorizationAction
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "2a58b7ce3cea"
down_revision: Union[str, None] = "d98efbda5e7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("scope", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("permissions", sa.ARRAY(sa.Integer), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "scope", name="uix_name_scope")
    )


def downgrade() -> None:
    op.drop_table("roles")
