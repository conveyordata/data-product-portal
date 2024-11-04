"""add databricks data output configuration

Revision ID: 2b47064c5d10
Revises: aeba8918cf93
Create Date: 2024-10-29 14:12:10.769015

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2b47064c5d10"
down_revision: Union[str, None] = "aeba8918cf93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_output_configurations", sa.Column("schema_path", sa.String))


def downgrade() -> None:
    op.drop_column("data_output_configuration", "schema_path")
