"""Refactored business area to domain

Revision ID: d98efbda5e7c
Revises: 33e853485942
Create Date: 2025-02-26 11:59:42.656312

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d98efbda5e7c"
down_revision: Union[str, None] = "33e853485942"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Migration steps:
def upgrade():
    op.rename_table("business_areas", "domains")
    op.alter_column("data_products", "business_area_id", new_column_name="domain_id")
    op.alter_column("datasets", "business_area_id", new_column_name="domain_id")


def downgrade():
    op.alter_column("data_products", "domain_id", new_column_name="business_area_id")
    op.alter_column("datasets", "domain_id", new_column_name="business_area_id")
    op.rename_table("domains", "business_areas")
