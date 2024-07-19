"""dataset type added

Revision ID: 6ea13dfa686f
Revises: 4e61079eaf16
Create Date: 2024-07-19 23:53:02.856064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.datasets.enums import DatasetType


# revision identifiers, used by Alembic.
revision: str = '6ea13dfa686f'
down_revision: Union[str, None] = '4e61079eaf16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "datasets",
        sa.Column("dataset_type", sa.String),
    )


def downgrade() -> None:
    op.drop_column("datasets", "dataset_type")

