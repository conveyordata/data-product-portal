"""Add data contracts

Revision ID: 5cece00a0dc3
Revises: 2b47064c5d10
Create Date: 2024-11-04 10:29:50.623004

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "5cece00a0dc3"
down_revision: Union[str, None] = "2b47064c5d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_contracts",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("data_output_id", sa.UUID, sa.ForeignKey("data_outputs.id")),
        sa.Column("table", sa.String),
        sa.Column("description", sa.String),
        sa.Column("checks", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "columns",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("data_contract_id", sa.UUID, sa.ForeignKey("data_contracts.id")),
        sa.Column("name", sa.String),
        sa.Column("description", sa.String),
        sa.Column("data_type", sa.String),
        sa.Column("checks", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "service_level_objectives",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("data_contract_id", sa.UUID, sa.ForeignKey("data_contracts.id")),
        sa.Column("type", sa.String),
        sa.Column("value", sa.String),
        sa.Column("severity", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("data_contracts")
    op.drop_table("columns")
    op.drop_table("service_level_objectives")
