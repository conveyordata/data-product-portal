"""split_input_ports_and_requests

Revision ID: aa9f983049d2
Revises: bef60a60b7e3
Create Date: 2026-07-13 15:22:40.184531

Splits the single ``input_ports`` table into:

* ``input_ports``          - the link (output port <-> consumer) + current access ``status``
* ``input_port_requests``  - one row per access request/decision (append-only history)

Per ADR-0021. This is the structural split only: the moved columns are copied into
one request row per existing link, then dropped from the link. The forward-looking fields
(``EXPIRED`` status, ``expiry_event_sent``, ``valid_from``/``valid_until``,
``access_duration_type``, ``requested_duration_days``) exist but stay inert on this
branch - nothing sets the time-bound / expiry ones yet.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "aa9f983049d2"
down_revision: Union[str, None] = "bef60a60b7e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UTCNOW = sa.text("timezone('utc'::text, CURRENT_TIMESTAMP)")


def upgrade() -> None:
    # 1. The new request table (one row per access request/decision).
    op.create_table(
        "input_port_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("input_port_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column("access_duration_type", sa.String(), nullable=False),
        sa.Column("requested_duration_days", sa.Integer(), nullable=True),
        sa.Column("requested_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "requested_on",
            sa.DateTime(timezone=False),
            server_default=UTCNOW,
            nullable=True,
        ),
        sa.Column("decided_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("decided_on", sa.DateTime(timezone=False), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=False),
            server_default=UTCNOW,
            nullable=True,
        ),
        sa.Column("updated_on", sa.DateTime(timezone=False), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )
    # At most one PENDING request per link.
    op.create_index(
        "uq_input_port_requests_one_pending_per_link",
        "input_port_requests",
        ["input_port_id"],
        unique=True,
        postgresql_where=sa.text("status = 'PENDING'"),
    )
    # Preserve the "denied requires a decision note" invariant on the request.
    op.create_check_constraint(
        "ck_input_port_requests_decision_note_required_when_denied",
        "input_port_requests",
        "status != 'DENIED' OR decision_note IS NOT NULL",
    )

    # 2. New link columns.
    op.add_column(
        "input_ports",
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column(
            "expiry_event_sent",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_input_ports_created_by_id_users",
        "input_ports",
        "users",
        ["created_by_id"],
        ["id"],
    )

    # 3. Backfill one request per existing link (link.status is still the enum here).
    op.execute(
        """
        INSERT INTO input_port_requests (
            id, input_port_id, status, justification, decision_note,
            access_duration_type, requested_duration_days,
            requested_by_id, requested_on, decided_by_id, decided_on,
            valid_from, valid_until, created_on, updated_on, deleted_at
        )
        SELECT
            gen_random_uuid(), ip.id, ip.status::text, ip.justification, ip.decision_note,
            'PERMANENT', NULL,
            ip.requested_by_id, ip.requested_on,
            CASE ip.status
                WHEN 'APPROVED' THEN ip.approved_by_id
                WHEN 'DENIED' THEN ip.denied_by_id
            END,
            CASE ip.status
                WHEN 'APPROVED' THEN ip.approved_on
                WHEN 'DENIED' THEN ip.denied_on
            END,
            NULL, NULL, ip.created_on, ip.updated_on, ip.deleted_at
        FROM input_ports ip
        """
    )

    # 4. Backfill the link's created_by from the original requester.
    op.execute("UPDATE input_ports SET created_by_id = requested_by_id")

    # 5. Drop the old decision-note check constraint (it moved to the request) so the
    #    status column can be converted and decision_note can be dropped.
    op.drop_constraint(
        "ck_input_ports_decision_note_required_when_denied",
        "input_ports",
        type_="check",
    )

    # 6. Convert the link status from the shared decisionstatus enum to a plain string
    #    so it can also carry 'EXPIRED'. The decisionstatus type stays (other tables use it).
    op.execute(
        "ALTER TABLE input_ports ALTER COLUMN status TYPE varchar USING status::text"
    )

    # 7. Drop the columns that now live on the request.
    op.drop_column("input_ports", "decision_note")
    op.drop_column("input_ports", "denied_on")
    op.drop_column("input_ports", "denied_by_id")
    op.drop_column("input_ports", "approved_on")
    op.drop_column("input_ports", "approved_by_id")
    op.drop_column("input_ports", "requested_on")
    op.drop_column("input_ports", "requested_by_id")
    op.drop_column("input_ports", "justification")


def downgrade() -> None:
    # 1. Re-add the moved columns to the link (nullable for now).
    op.add_column("input_ports", sa.Column("justification", sa.Text(), nullable=True))
    op.add_column(
        "input_ports",
        sa.Column("requested_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column(
            "requested_on",
            sa.DateTime(timezone=False),
            server_default=UTCNOW,
            nullable=True,
        ),
    )
    op.add_column(
        "input_ports",
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("approved_on", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("denied_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("denied_on", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column("input_ports", sa.Column("decision_note", sa.Text(), nullable=True))
    op.create_foreign_key(
        "input_ports_requested_by_id_fkey",
        "input_ports",
        "users",
        ["requested_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "input_ports_approved_by_id_fkey",
        "input_ports",
        "users",
        ["approved_by_id"],
        ["id"],
    )
    op.create_foreign_key(
        "input_ports_denied_by_id_fkey",
        "input_ports",
        "users",
        ["denied_by_id"],
        ["id"],
    )

    # 2. Backfill the link columns from each link's (single) request.
    op.execute(
        """
        UPDATE input_ports ip SET
            justification = r.justification,
            requested_by_id = r.requested_by_id,
            requested_on = r.requested_on,
            decision_note = r.decision_note,
            approved_by_id = CASE WHEN r.status = 'APPROVED' THEN r.decided_by_id END,
            approved_on = CASE WHEN r.status = 'APPROVED' THEN r.decided_on END,
            denied_by_id = CASE WHEN r.status = 'DENIED' THEN r.decided_by_id END,
            denied_on = CASE WHEN r.status = 'DENIED' THEN r.decided_on END
        FROM input_port_requests r
        WHERE r.input_port_id = ip.id
        """
    )

    # 3. Convert the link status back to the decisionstatus enum (EXPIRED -> APPROVED).
    op.execute(
        "ALTER TABLE input_ports "
        "ALTER COLUMN status TYPE decisionstatus "
        "USING (CASE WHEN status = 'EXPIRED' THEN 'APPROVED' ELSE status END)::decisionstatus"
    )

    # 4. Restore justification NOT NULL and the decision-note check constraint.
    op.execute(
        "UPDATE input_ports SET justification = 'No justification provided (migration)' "
        "WHERE justification IS NULL"
    )
    op.alter_column("input_ports", "justification", nullable=False)
    op.create_check_constraint(
        "ck_input_ports_decision_note_required_when_denied",
        "input_ports",
        "status != 'DENIED' OR decision_note IS NOT NULL",
    )

    # 5. Drop the new link columns.
    op.drop_constraint(
        "fk_input_ports_created_by_id_users", "input_ports", type_="foreignkey"
    )
    op.drop_column("input_ports", "expiry_event_sent")
    op.drop_column("input_ports", "created_by_id")

    # 6. Drop the request table.
    op.drop_table("input_port_requests")
