"""add namespace, status and finalizers to domains

Revision ID: 3d9c51e0a7b2
Revises: b71a5f3e29cd
Create Date: 2026-10-19 12:00:00.000000

"""

import re
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.settings import settings

revision: str = "3d9c51e0a7b2"
down_revision: Union[str, None] = "b71a5f3e29cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NAMESPACE_MAX_LENGTH = settings.NAMESPACE_MAX_LENGTH


# Frozen copy of ResourceNameService._resource_name_from_name
def _namespace_from_name(name: str) -> str:
    namespace = re.sub(
        r"[^a-z0-9+=,.@_-]", "", (name or "").lower().replace(" ", "-")
    ).strip("-")
    return namespace[:NAMESPACE_MAX_LENGTH]


def _unique(base: str, taken: set[str]) -> str:
    candidate, n = base, 2
    while candidate in taken:
        suffix = f"-{n}"
        candidate = base[: NAMESPACE_MAX_LENGTH - len(suffix)] + suffix
        n += 1
    return candidate


def upgrade() -> None:
    op.add_column("domains", sa.Column("namespace", sa.String(), nullable=True))
    op.add_column(
        "domains",
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
    )
    op.add_column(
        "domains",
        sa.Column(
            "finalizers",
            postgresql.ARRAY(sa.String()),
            nullable=False,
            server_default="{}",
        ),
    )

    conn = op.get_bind()
    taken: set[str] = set()
    for id_, name in conn.execute(
        sa.text("SELECT id, name FROM domains ORDER BY created_on, id")
    ):
        namespace = _unique(_namespace_from_name(name) or str(id_), taken)
        taken.add(namespace)
        conn.execute(
            sa.text("UPDATE domains SET namespace = :namespace WHERE id = :id"),
            {"namespace": namespace, "id": id_},
        )

    op.alter_column("domains", "namespace", nullable=False)
    op.create_unique_constraint("uq_domains_namespace", "domains", ["namespace"])


def downgrade() -> None:
    op.drop_constraint("uq_domains_namespace", "domains", type_="unique")
    op.drop_column("domains", "finalizers")
    op.drop_column("domains", "status")
    op.drop_column("domains", "namespace")
