"""User unique external_id

Revision ID: ae23301a4a69
Revises: 676a29542f0b
Create Date: 2026-09-04 09:35:17.028747

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ae23301a4a69"
down_revision: Union[str, None] = "676a29542f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_users_external_id", "users", ["external_id"])


def downgrade() -> None:
    op.drop_constraint("uq_users_external_id", "users")
