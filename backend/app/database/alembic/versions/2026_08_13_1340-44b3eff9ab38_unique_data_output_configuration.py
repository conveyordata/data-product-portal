"""Unique data output configuration

Revision ID: 44b3eff9ab38
Revises: 12cb16f491cd
Create Date: 2026-08-13 13:40:21.607879

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "44b3eff9ab38"
down_revision: Union[str, None] = "12cb16f491cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_data_outputs_configuration", "data_outputs", ["configuration_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_data_outputs_configuration", "data_outputs", type_="unique")
