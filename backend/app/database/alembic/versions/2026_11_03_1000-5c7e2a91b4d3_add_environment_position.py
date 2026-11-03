from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "5c7e2a91b4d3"
down_revision: Union[str, None] = "f9c2a3a993da"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("environments", sa.Column("position", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("environments", "position")
