"""add snowflake data output configuration

Revision ID: aeba8918cf93
Revises: 4b87ab41d95e
Create Date: 2024-10-29 09:47:11.809875

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aeba8918cf93"
down_revision: Union[str, None] = "4b87ab41d95e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_output_configurations", sa.Column("schema", sa.String))
    op.add_column("data_output_configurations", sa.Column("schema_suffix", sa.String))


def downgrade() -> None:
    op.drop_column("data_output_configurations", "schema")
    op.drop_column("data_output_configurations", "schema_suffix")
