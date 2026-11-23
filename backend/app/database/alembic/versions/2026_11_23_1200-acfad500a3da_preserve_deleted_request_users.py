from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "acfad500a3da"
down_revision: Union[str, None] = "5c7e2a91b4d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

USER_REFERENCES = [
    ("role_assignments_data_product", "requested_by", True),
    ("role_assignments_data_product", "decided_by", True),
    ("role_assignments_dataset", "requested_by", True),
    ("role_assignments_dataset", "decided_by", True),
    ("role_assignments_global", "requested_by", True),
    ("role_assignments_global", "decided_by", True),
    ("input_port_requests", "requested_by", True),
    ("input_port_requests", "decided_by", True),
    ("input_port_requests", "revoked_by", True),
    ("data_outputs_datasets", "requested_by", False),
    ("data_outputs_datasets", "approved_by", False),
    ("data_outputs_datasets", "denied_by", False),
    ("explorations", "owner", True),
]


def upgrade() -> None:
    for table, field, has_fkey in USER_REFERENCES:
        op.add_column(
            table,
            sa.Column(f"deleted_{field}_identifier", sa.String(), nullable=True),
        )
        if has_fkey:
            op.drop_constraint(f"{table}_{field}_id_fkey", table, type_="foreignkey")


def downgrade() -> None:
    connection = op.get_bind()
    users = sa.table("users", sa.column("id", sa.UUID), sa.column("email", sa.String))
    system_actor_id = connection.scalar(
        sa.select(users.c.id).where(users.c.email == "systemaccount@noreply.com")
    )
    for table, field, has_fkey in USER_REFERENCES:
        if has_fkey:
            rows = sa.table(table, sa.column(f"{field}_id", sa.UUID))
            column = rows.c[f"{field}_id"]
            orphaned = column.is_not(None) & column.not_in(sa.select(users.c.id))
            if connection.scalar(sa.select(column).where(orphaned).limit(1)):
                if system_actor_id is None:
                    raise RuntimeError(
                        f"Cannot downgrade orphaned {table}.{field}_id without "
                        "system account systemaccount@noreply.com"
                    )
                connection.execute(
                    rows.update().where(orphaned).values({column: system_actor_id})
                )
            op.create_foreign_key(
                f"{table}_{field}_id_fkey", table, "users", [f"{field}_id"], ["id"]
            )
        op.drop_column(table, f"deleted_{field}_identifier")
