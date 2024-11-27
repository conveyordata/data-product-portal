"""api keys

Revision ID: 1b1a684fc8df
Revises: 3d6be1e9b5fa
Create Date: 2024-11-27 15:26:12.214249

"""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1b1a684fc8df"
down_revision: Union[str, None] = "3d6be1e9b5fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_products",
        sa.Column("api_key", sa.UUID, server_default=sa.text("gen_random_uuid()")),
    )
    op.execute(
        f"""
    INSERT INTO public.users
(email, id, external_id, first_name, last_name, created_on, is_admin)
VALUES('projectaccount@noreply.com', '{uuid4()}', 'projectaccount_bot',
'Projectaccount', 'Bot', timezone('utc'::text, CURRENT_TIMESTAMP), false);
"""
    )


def downgrade() -> None:
    op.drop_column("data_products", "api_key")
    op.execute(
        """DELETE FROM public.users WHERE email = 'projectaccount@noreply.com'"""
    )
