from typing import Sequence, Union
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision: str = "d5ff4d3a20d6"
down_revision: Union[str, None] = "5c7e2a91b4d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DELETED_USER_ID = UUID("6183c216-de6a-4045-b102-04ee611b79c7")

USER_REFERENCES = [
    ("role_assignments_data_product", "requested_by_id"),
    ("role_assignments_data_product", "decided_by_id"),
    ("role_assignments_dataset", "requested_by_id"),
    ("role_assignments_dataset", "decided_by_id"),
    ("role_assignments_global", "requested_by_id"),
    ("role_assignments_global", "decided_by_id"),
    ("input_port_requests", "requested_by_id"),
    ("input_port_requests", "decided_by_id"),
    ("input_port_requests", "revoked_by_id"),
    ("data_outputs_datasets", "requested_by_id"),
    ("data_outputs_datasets", "approved_by_id"),
    ("data_outputs_datasets", "denied_by_id"),
    ("explorations", "owner_id"),
]

identities = sa.table(
    "identities",
    sa.column("id", sa.UUID),
    sa.column("type", sa.String),
    sa.column("external_id", sa.String),
)
users = sa.table(
    "users",
    sa.column("id", sa.UUID),
    sa.column("email", sa.String),
    sa.column("first_name", sa.String),
    sa.column("last_name", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        identities,
        [
            {
                "id": DELETED_USER_ID,
                "type": "user",
                "external_id": f"deleted-user-{DELETED_USER_ID}",
            }
        ],
    )
    op.bulk_insert(
        users,
        [
            {
                "id": DELETED_USER_ID,
                "email": "deleted-user@example.com",
                "first_name": "Deleted",
                "last_name": "user",
            }
        ],
    )


def downgrade() -> None:
    connection = op.get_bind()
    system_account_id = connection.scalar(
        sa.select(users.c.id).where(users.c.email == "systemaccount@noreply.com")
    )
    for table, column in USER_REFERENCES:
        references = sa.table(table, sa.column(column, sa.UUID))
        connection.execute(
            references.update()
            .where(references.c[column] == DELETED_USER_ID)
            .values({column: system_account_id})
        )
    connection.execute(identities.delete().where(identities.c.id == DELETED_USER_ID))
