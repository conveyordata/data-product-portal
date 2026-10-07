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
    events = sa.table("events", sa.column("actor_id", sa.UUID))
    users = sa.table("users", sa.column("id", sa.UUID), sa.column("email", sa.String))
    orphaned_actors = events.c.actor_id.not_in(sa.select(users.c.id))
    connection = op.get_bind()
    if connection.scalar(sa.select(events.c.actor_id).where(orphaned_actors).limit(1)):
        system_actor_id = connection.scalar(
            sa.select(users.c.id).where(users.c.email == "systemaccount@noreply.com")
        )
        if system_actor_id is None:
            raise RuntimeError(
                "Cannot downgrade orphaned events without system account "
                "systemaccount@noreply.com"
            )
        connection.execute(
            events.update().where(orphaned_actors).values(actor_id=system_actor_id)
        )
    op.create_foreign_key(
        "events_actor_id_fkey", "events", "users", ["actor_id"], ["id"]
    )
    op.drop_column("events", "deleted_actor_identifier")
