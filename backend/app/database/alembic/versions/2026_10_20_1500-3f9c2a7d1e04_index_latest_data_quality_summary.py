from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "3f9c2a7d1e04"
down_revision: Union[str, None] = "a82c9b3e7d41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_output_port_data_quality_summaries_latest",
        "output_port_data_quality_summaries",
        ["output_port_id", sa.text("created_at DESC"), sa.text("id DESC")],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_output_port_data_quality_summaries_latest",
        table_name="output_port_data_quality_summaries",
    )
