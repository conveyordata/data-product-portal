from typing import Sequence, Union

from alembic import op

revision: str = "f9c2a3a993da"
down_revision: Union[str, None] = "a9203b7e41cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FOREIGN_KEYS = [
    ("tags_data_products", "data_product_id", "data_products"),
    ("tags_data_products", "tag_id", "tags"),
    ("tags_datasets", "dataset_id", "datasets"),
    ("tags_datasets", "tag_id", "tags"),
    ("tags_data_outputs", "data_output_id", "data_outputs"),
    ("tags_data_outputs", "tag_id", "tags"),
]


def upgrade() -> None:
    _recreate_foreign_keys(ondelete="CASCADE")


def downgrade() -> None:
    _recreate_foreign_keys(ondelete=None)


def _recreate_foreign_keys(ondelete: str | None) -> None:
    for table, column, referred_table in FOREIGN_KEYS:
        name = f"{table}_{column}_fkey"
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(
            name, table, referred_table, [column], ["id"], ondelete=ondelete
        )
