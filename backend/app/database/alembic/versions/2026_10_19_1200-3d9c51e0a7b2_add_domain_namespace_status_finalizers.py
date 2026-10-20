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
    ).strip("-")[:NAMESPACE_MAX_LENGTH]
    return "" if set(namespace) <= {"."} else namespace


# FOR SHARE conflicts with the FOR UPDATE lock DomainService takes before deleting,
# so writes outside the API cannot slip a Data Product into a deleting Domain either
REJECT_DELETING_DOMAIN = """
CREATE FUNCTION reject_assignment_to_deleting_domain() RETURNS trigger AS $$
DECLARE
    domain_status text;
BEGIN
    IF TG_OP = 'INSERT' OR NEW.domain_id IS DISTINCT FROM OLD.domain_id THEN
        SELECT status INTO domain_status FROM domains
        WHERE id = NEW.domain_id
        FOR SHARE;
        IF domain_status = 'deleting' THEN
            RAISE EXCEPTION 'Domain % is pending deletion', NEW.domain_id
                USING ERRCODE = 'check_violation';
        END IF;
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER reject_assignment_to_deleting_domain
BEFORE INSERT OR UPDATE OF domain_id ON abstract_data_products
FOR EACH ROW EXECUTE FUNCTION reject_assignment_to_deleting_domain();
"""


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
    op.execute(REJECT_DELETING_DOMAIN)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER reject_assignment_to_deleting_domain ON abstract_data_products"
    )
    op.execute("DROP FUNCTION reject_assignment_to_deleting_domain()")
    op.drop_constraint("uq_domains_namespace", "domains", type_="unique")
    op.drop_column("domains", "finalizers")
    op.drop_column("domains", "status")
    op.drop_column("domains", "namespace")
