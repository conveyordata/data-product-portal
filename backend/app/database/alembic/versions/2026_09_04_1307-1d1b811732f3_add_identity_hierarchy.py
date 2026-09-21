"""add identity hierarchy

Revision ID: 1d1b811732f3
Revises: c2a4e91f7b3d
Create Date: 2026-09-04 13:07:24.707189
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "1d1b811732f3"
down_revision: Union[str, None] = "c2a4e91f7b3d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "identities",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=False),
            server_default=utcnow(),
        ),
        sa.Column("updated_on", sa.DateTime(timezone=False)),
        sa.CheckConstraint(
            "type IN ('user', 'group', 'machine_user')",
            name="ck_identities_type",
        ),
        sa.UniqueConstraint(
            "type",
            "external_id",
            name="uq_identities_type_external_id",
        ),
    )

    op.execute(
        """
        INSERT INTO identities (
            id,
            type,
            external_id,
            created_on,
            updated_on
        )
        SELECT
            id,
            'user',
            COALESCE(external_id, id::text),
            created_on,
            updated_on
        FROM users
        """
    )

    op.create_foreign_key(
        "fk_users_id_identities",
        "users",
        "identities",
        ["id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_column("users", "external_id")
    op.drop_column("users", "created_on")
    op.drop_column("users", "updated_on")

    op.create_table(
        "groups",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("identities.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("display_name", sa.String(), nullable=False),
    )

    op.create_table(
        "machine_users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("identities.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("display_name", sa.String(), nullable=False),
    )

    op.create_table(
        "group_memberships",
        sa.Column(
            "group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("groups.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "member_identity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("identities.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "created_on",
            sa.DateTime(timezone=False),
            server_default=utcnow(),
        ),
        sa.Column("updated_on", sa.DateTime(timezone=False)),
        sa.CheckConstraint(
            "group_id <> member_identity_id",
            name="ck_group_memberships_not_self",
        ),
    )


def downgrade() -> None:
    op.drop_table("group_memberships")
    op.drop_table("machine_users")
    op.drop_table("groups")

    op.add_column(
        "users",
        sa.Column("external_id", sa.String(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "created_on",
            sa.DateTime(timezone=False),
            server_default=utcnow(),
        ),
    )
    op.add_column(
        "users",
        sa.Column("updated_on", sa.DateTime(timezone=False)),
    )

    op.execute(
        """
        UPDATE users
        SET
            external_id = identities.external_id,
            created_on = identities.created_on,
            updated_on = identities.updated_on
        FROM identities
        WHERE users.id = identities.id
        """
    )

    op.create_unique_constraint(
        "uq_users_external_id",
        "users",
        ["external_id"],
    )

    op.drop_constraint(
        "fk_users_id_identities",
        "users",
        type_="foreignkey",
    )
    op.drop_table("identities")
