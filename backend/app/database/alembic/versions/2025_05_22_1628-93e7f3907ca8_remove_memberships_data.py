"""Remove memberships data

Revision ID: 93e7f3907ca8
Revises: 6441623a586b
Create Date: 2025-05-22 16:28:46.744343

"""

from enum import UNIQUE, Enum, StrEnum, verify
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

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


class DataProductUserRole(str, Enum):
    OWNER = "owner"
    MEMBER = "member"


def upgrade():
    op.drop_table("data_product_memberships")


def downgrade():
    op.create_table(
        "data_product_memberships",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "role",
            sa.Enum("owner", "member", name="dataproductuserrole"),
            nullable=False,
            server_default="member",
        ),
        sa.Column(
            "data_product_id", UUID(as_uuid=True), sa.ForeignKey("data_products.id")
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "role", sa.Enum(DataProductUserRole), default=DataProductUserRole.MEMBER
        ),
        sa.Column(
            "status",
            sa.Enum(name="decisionstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("requested_by_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("approved_by_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("approved_on", sa.DateTime(timezone=False)),
        sa.Column("denied_by_id", UUID, sa.ForeignKey("users.id")),
        sa.Column("denied_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table("data_product_memberships")
