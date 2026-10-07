from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b71a5f3e29cd"
down_revision: Union[str, None] = "3f1c2b7a9d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "events", sa.Column("deleted_actor_identifier", sa.String(), nullable=True)
    )
    op.drop_constraint("events_actor_id_fkey", "events", type_="foreignkey")


def downgrade() -> None:
    op.execute(
        "UPDATE events SET actor_id = NULL WHERE actor_id NOT IN (SELECT id FROM users)"
    )
    op.create_foreign_key(
        "events_actor_id_fkey", "events", "users", ["actor_id"], ["id"]
    )
    op.drop_column("events", "deleted_actor_identifier")
