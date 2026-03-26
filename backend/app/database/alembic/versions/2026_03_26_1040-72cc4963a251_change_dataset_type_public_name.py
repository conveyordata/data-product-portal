"""change dataset type public name

Revision ID: 72cc4963a251
Revises: d838b01d5e6a
Create Date: 2026-03-26 10:40:02.796058

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "72cc4963a251"
down_revision: Union[str, None] = "d838b01d5e6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "datasets",
        "access_type",
        existing_type=sa.Enum(
            "public", "restricted", "private", name="outputportaccesstype"
        ),
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="access_type::text",
    )
    op.execute(sa.text("DROP TYPE IF EXISTS outputportaccesstype"))
    op.execute(
        sa.text(
            "UPDATE datasets SET access_type = 'unrestricted' WHERE access_type = 'public'"
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE datasets SET access_type = 'public' WHERE access_type = 'unrestricted'"
        )
    )
    outputportaccesstype = sa.Enum(
        "public", "restricted", "private", name="outputportaccesstype"
    )
    outputportaccesstype.create(op.get_bind())
    op.alter_column(
        "datasets",
        "access_type",
        existing_type=sa.String(),
        type_=outputportaccesstype,
        existing_nullable=True,
        postgresql_using="access_type::outputportaccesstype",
    )
