"""create embeddings

Revision ID: 638303a2cb77
Revises: bb31223f935e
Create Date: 2026-02-23 18:09:17.390671

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import orm

from app.data_products.output_ports.service import OutputPortService

# revision identifiers, used by Alembic.
revision: str = "638303a2cb77"
down_revision: Union[str, None] = "bb31223f935e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    OutputPortService(session).recalculate_search_for_all_output_ports()


def downgrade() -> None:
    pass
