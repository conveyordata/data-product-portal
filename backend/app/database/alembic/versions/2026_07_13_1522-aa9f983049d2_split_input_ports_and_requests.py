"""split_input_ports_and_requests

Revision ID: aa9f983049d2
Revises: bef60a60b7e3
Create Date: 2026-07-13 15:22:40.184531

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
    op.create_table(
        "input_port_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "input_port_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("input_ports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("decision_note", sa.Text(), nullable=True),
        sa.Column("access_duration_type", sa.String(), nullable=False),
        sa.Column("requested_duration_days", sa.Integer(), nullable=True),
        sa.Column(
            "requested_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "requested_on",
            sa.DateTime(timezone=False),
            server_default=UTCNOW,
            nullable=True,
        ),
        sa.Column(
            "decided_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
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
    )
    op.create_index(
        "uq_input_port_requests_one_pending_per_link",
        "input_port_requests",
        ["input_port_id"],
        unique=True,
        postgresql_where=sa.text("decision = 'PENDING'"),
    )
    op.create_check_constraint(
        "ck_input_port_requests_decision_note_required_when_denied",
        "input_port_requests",
        "decision != 'DENIED' OR decision_note IS NOT NULL",
    )
    op.execute(
        """
        INSERT INTO input_port_requests (id, input_port_id, decision, justification, decision_note,
                                         access_duration_type, requested_duration_days,
                                         requested_by_id, requested_on, decided_by_id, decided_on,
                                         valid_from, valid_until, created_on, updated_on)
        SELECT gen_random_uuid(),
               ip.id,
               ip.status::text,
               ip.justification,
               ip.decision_note,
               'PERMANENT',
               NULL,
               ip.requested_by_id,
               ip.requested_on,
               CASE ip.status
                   WHEN 'APPROVED' THEN ip.approved_by_id
                   WHEN 'DENIED' THEN ip.denied_by_id
                   END,
               CASE ip.status
                   WHEN 'APPROVED' THEN ip.approved_on
                   WHEN 'DENIED' THEN ip.denied_on
                   END,
               CASE ip.status
                   WHEN 'APPROVED' THEN ip.approved_on
                   END,
               NULL,
               ip.created_on,
               ip.updated_on
        FROM input_ports ip
        """
    )
    op.drop_constraint(
        "ck_input_ports_decision_note_required_when_denied",
        "input_ports",
        type_="check",
    )
    op.execute(
        "ALTER TABLE input_ports ALTER COLUMN status TYPE varchar USING status::text"
    )
    op.drop_column("input_ports", "decision_note")
    op.drop_column("input_ports", "denied_on")
    op.drop_column("input_ports", "denied_by_id")
    op.drop_column("input_ports", "approved_on")
    op.drop_column("input_ports", "approved_by_id")
    op.drop_column("input_ports", "requested_on")
    op.drop_column("input_ports", "requested_by_id")
    op.drop_column("input_ports", "justification")


def downgrade() -> None:
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
    op.execute(
        """
        UPDATE input_ports ip
        SET justification   = r.justification,
            requested_by_id = r.requested_by_id,
            requested_on    = r.requested_on,
            decision_note   = r.decision_note,
            approved_by_id  = CASE WHEN r.decision = 'APPROVED' THEN r.decided_by_id END,
            approved_on     = CASE WHEN r.decision = 'APPROVED' THEN r.decided_on END,
            denied_by_id    = CASE WHEN r.decision = 'DENIED' THEN r.decided_by_id END,
            denied_on       = CASE WHEN r.decision = 'DENIED' THEN r.decided_on END
        FROM input_port_requests r
        WHERE r.input_port_id = ip.id
        """
    )
    op.execute(
        "ALTER TABLE input_ports "
        "ALTER COLUMN status TYPE decisionstatus "
        "USING (CASE WHEN status = 'EXPIRED' THEN 'APPROVED' ELSE status END)::decisionstatus"
    )
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
    op.drop_table("input_port_requests")
