"""add system user

Revision ID: 79a3d8a69dec
Revises: c6554418a88d
Create Date: 2024-10-08 13:41:04.741291

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "79a3d8a69dec"
down_revision: Union[str, None] = "c6554418a88d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    id = uuid4()
    op.execute(
        "INSERT INTO users (id, email, external_id, first_name, last_name, is_admin)"
        f" VALUES('{id}',"
        "'systemaccount@noreply.com','systemaccount_bot', 'Systemaccount', 'Bot', true)"
    )


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE external_id='systemaccount_bot'")
