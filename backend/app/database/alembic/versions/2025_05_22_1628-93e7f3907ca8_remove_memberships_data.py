"""Remove memberships data

Revision ID: 93e7f3907ca8
Revises: 6441623a586b
Create Date: 2025-05-22 16:28:46.744343

"""

from enum import UNIQUE, StrEnum, verify
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow  # for server_default

# revision identifiers, used by Alembic.
revision: str = "93e7f3907ca8"
down_revision: Union[str, None] = "6441623a586b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


@verify(UNIQUE)
class DecisionStatus(StrEnum):
    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"


def upgrade():
    op.drop_table("data_product_memberships")


def downgrade():
    op.create_table(
        "data_product_memberships",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "role",
            sa.Enum("owner", "member", name="dataproductuserrole"),
            nullable=False,
            server_default="member",
        ),
        sa.Column(
            "status",
            sa.Enum(name="decisionstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("approved_on", sa.DateTime(timezone=False), nullable=True),
        sa.Column("denied_on", sa.DateTime(timezone=False), nullable=True),
        sa.Column("data_product_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("approved_by_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("denied_by_id", sa.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["data_product_id"],
            ["data_products.id"],
            name="fk_data_product_memberships_data_product_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_data_product_memberships_user_id"
        ),
        sa.ForeignKeyConstraint(
            ["requested_by_id"],
            ["users.id"],
            name="fk_data_product_memberships_requested_by_id",
        ),
        sa.ForeignKeyConstraint(
            ["approved_by_id"],
            ["users.id"],
            name="fk_data_product_memberships_approved_by_id",
        ),
        sa.ForeignKeyConstraint(
            ["denied_by_id"],
            ["users.id"],
            name="fk_data_product_memberships_denied_by_id",
        ),
        sa.UniqueConstraint(
            "data_product_id", "user_id", name="unique_data_product_user"
        ),
    )
