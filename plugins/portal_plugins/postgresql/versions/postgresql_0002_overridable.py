from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "postgresql_0002_overridable"
down_revision: Union[str, None] = "postgresql_0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "postgresql_technical_asset_configurations"


def upgrade() -> None:
    op.add_column(TABLE, sa.Column("engine_version", sa.String(), server_default="16"))
    op.add_column(TABLE, sa.Column("size", sa.String(), server_default="small"))
    op.add_column(TABLE, sa.Column("storage_gb", sa.String(), server_default="20"))


def downgrade() -> None:
    op.drop_column(TABLE, "storage_gb")
    op.drop_column(TABLE, "size")
    op.drop_column(TABLE, "engine_version")
