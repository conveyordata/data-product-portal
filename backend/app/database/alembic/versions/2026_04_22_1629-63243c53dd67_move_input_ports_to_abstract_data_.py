"""move input ports to abstract data products

Revision ID: 63243c53dd67
Revises: d6286ec9911b
Create Date: 2026-04-22 16:29:20.380623

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "63243c53dd67"
down_revision: Union[str, None] = "d6286ec9911b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("data_products_datasets", "input_ports")
    op.drop_constraint(
        "data_products_datasets_data_product_id_fkey",
        "input_ports",
        type_="foreignkey",
    )
    op.alter_column(
        "input_ports",
        "data_product_id",
        new_column_name="consuming_abstract_data_product_id",
    )
    op.create_foreign_key(
        "input_ports_consuming_abstract_data_product_id_fkey",
        "input_ports",
        "abstract_data_products",
        ["consuming_abstract_data_product_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "input_ports_consuming_abstract_data_product_id_fkey",
        "input_ports",
        type_="foreignkey",
    )
    op.alter_column(
        "input_ports",
        "consuming_abstract_data_product_id",
        new_column_name="data_product_id",
    )
    op.create_foreign_key(
        "data_products_datasets_data_product_id_fkey",
        "input_ports",
        "data_products",
        ["data_product_id"],
        ["id"],
    )
    op.rename_table("input_ports", "data_products_datasets")
