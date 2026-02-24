"""Index on dataset data_product_id

Revision ID: c6bf8bf62e6e
Revises: bb31223f935e
Create Date: 2026-02-23 17:18:31.191466

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c6bf8bf62e6e"
down_revision: Union[str, None] = "bb31223f935e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_data_products_domain", "data_products", ["domain_id"], unique=False
    )
    op.create_index(
        "idx_dataset_data_product_id", "datasets", ["data_product_id"], unique=False
    )
    op.create_index(
        "idx_data_products_datasets_dp",
        "data_products_datasets",
        ["data_product_id"],
        unique=False,
    )
    op.create_index(
        "idx_data_products_datasets_ds",
        "data_products_datasets",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "idx_data_outputs_data_product_id", "data_outputs", ["owner_id"], unique=False
    )
    op.create_index(
        "idx_role_assignments_dataset",
        "role_assignments_dataset",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "idx_role_assignments_data_product",
        "role_assignments_data_product",
        ["data_product_id"],
        unique=False,
    )
    op.create_index(
        "idx_tags_data_products",
        "tags_data_products",
        ["data_product_id"],
        unique=False,
    )
    op.create_index(
        "idx_tags_data_products_tag_id", "tags_data_products", ["tag_id"], unique=False
    )
    op.create_index("idx_tags_datasets", "tags_datasets", ["dataset_id"], unique=False)
    op.create_index(
        "idx_tags_datasets_tag_id", "tags_datasets", ["tag_id"], unique=False
    )
    op.create_index(
        "idx_data_products_settings_values_datasets",
        "data_products_settings_values",
        ["dataset_id"],
        unique=False,
    )
    op.create_index(
        "idx_data_products_settings_values_data_products",
        "data_products_settings_values",
        ["data_product_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_data_products_domain", table_name="data_products")
    op.drop_index("idx_dataset_data_product_id", table_name="datasets")
    op.drop_index("idx_data_products_datasets_dp", table_name="data_products_datasets")
    op.drop_index("idx_data_products_datasets_ds", table_name="data_products_datasets")
    op.drop_index("idx_data_outputs_data_product_id", table_name="datasets")
    op.drop_index(
        "idx_role_assignments_dataset", table_name="role_assignments_data_product"
    )
    op.drop_index(
        "idx_role_assignments_data_product", table_name="role_assignments_data_product"
    )
    op.drop_index("idx_tags_data_products", table_name="tags_data_products")
    op.drop_index("idx_tags_data_products_tag_id", table_name="tags_data_products")
    op.drop_index("idx_tags_datasets", table_name="tags_datasets")
    op.drop_index("idx_tags_datasets_tag_id", table_name="tags_datasets")
    op.drop_index(
        "idx_data_products_settings_values_datasets",
        table_name="data_products_settings_values",
    )
    op.drop_index(
        "idx_data_products_settings_values_data_products",
        table_name="data_products_settings_values",
    )
