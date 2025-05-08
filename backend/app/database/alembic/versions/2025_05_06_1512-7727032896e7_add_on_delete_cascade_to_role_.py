"""Add ON DELETE CASCADE to role assignment FKs

Revision ID: 7727032896e7
Revises: 886fc49acbda
Create Date: 2025-05-06 15:12:55.541910

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7727032896e7"
down_revision: Union[str, None] = "886fc49acbda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        "ALTER TABLE role_assignments_dataset "
        "DROP CONSTRAINT role_assignments_dataset_dataset_id_fkey, "
        "ADD CONSTRAINT role_assignments_dataset_dataset_id_fkey "
        "FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE;"
    )
    op.execute(
        "ALTER TABLE role_assignments_data_product "
        "DROP CONSTRAINT role_assignments_data_product_data_product_id_fkey, "
        "ADD CONSTRAINT role_assignments_data_product_data_product_id_fkey "
        "FOREIGN KEY (data_product_id) REFERENCES data_products(id) ON DELETE CASCADE;"
    )


def downgrade():
    op.execute(
        "ALTER TABLE role_assignments_dataset "
        "DROP CONSTRAINT role_assignments_dataset_dataset_id_fkey, "
        "ADD CONSTRAINT role_assignments_dataset_dataset_id_fkey "
        "FOREIGN KEY (dataset_id) REFERENCES datasets(id);"
    )
    op.execute(
        "ALTER TABLE role_assignments_data_product "
        "DROP CONSTRAINT role_assignments_data_product_data_product_id_fkey, "
        "ADD CONSTRAINT role_assignments_data_product_data_product_id_fkey "
        "FOREIGN KEY (data_product_id) REFERENCES data_products(id);"
    )
