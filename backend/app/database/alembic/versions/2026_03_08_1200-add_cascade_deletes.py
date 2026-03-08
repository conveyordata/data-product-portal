"""Add CASCADE to foreign keys for delete operations

Revision ID: a1b2c3d4e5f6
Revises: 491c8783a7bc
Create Date: 2026-03-08 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "491c8783a7bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Each tuple: (constraint_name, source_table, source_col, target_table, target_col)
FK_CONSTRAINTS = [
    (
        "fk_datasets_data_product_id_data_products",
        "datasets",
        "data_product_id",
        "data_products",
        "id",
    ),
    (
        "data_products_datasets_data_product_id_fkey",
        "data_products_datasets",
        "data_product_id",
        "data_products",
        "id",
    ),
    (
        "data_products_datasets_dataset_id_fkey",
        "data_products_datasets",
        "dataset_id",
        "datasets",
        "id",
    ),
    (
        "data_outputs_owner_id_fkey",
        "data_outputs",
        "owner_id",
        "data_products",
        "id",
    ),
    (
        "data_outputs_datasets_data_output_id_fkey",
        "data_outputs_datasets",
        "data_output_id",
        "data_outputs",
        "id",
    ),
    (
        "data_outputs_datasets_dataset_id_fkey",
        "data_outputs_datasets",
        "dataset_id",
        "datasets",
        "id",
    ),
    (
        "tags_data_products_data_product_id_fkey",
        "tags_data_products",
        "data_product_id",
        "data_products",
        "id",
    ),
    (
        "tags_data_products_tag_id_fkey",
        "tags_data_products",
        "tag_id",
        "tags",
        "id",
    ),
    (
        "tags_datasets_dataset_id_fkey",
        "tags_datasets",
        "dataset_id",
        "datasets",
        "id",
    ),
    (
        "tags_datasets_tag_id_fkey",
        "tags_datasets",
        "tag_id",
        "tags",
        "id",
    ),
    (
        "tags_data_outputs_data_output_id_fkey",
        "tags_data_outputs",
        "data_output_id",
        "data_outputs",
        "id",
    ),
    (
        "tags_data_outputs_tag_id_fkey",
        "tags_data_outputs",
        "tag_id",
        "tags",
        "id",
    ),
    (
        "dataset_query_stats_daily_consumer_data_product_id_fkey",
        "dataset_query_stats_daily",
        "consumer_data_product_id",
        "data_products",
        "id",
    ),
]


def upgrade() -> None:
    for constraint_name, source_table, source_col, target_table, target_col in FK_CONSTRAINTS:
        op.drop_constraint(constraint_name, source_table, type_="foreignkey")
        op.create_foreign_key(
            constraint_name,
            source_table,
            target_table,
            [source_col],
            [target_col],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    for constraint_name, source_table, source_col, target_table, target_col in FK_CONSTRAINTS:
        op.drop_constraint(constraint_name, source_table, type_="foreignkey")
        op.create_foreign_key(
            constraint_name,
            source_table,
            target_table,
            [source_col],
            [target_col],
        )
