"""add data_product_id to dataset

Revision ID: d56d796fb20d
Revises: 0358e660a680
Create Date: 2025-10-03 12:51:14.866274

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d56d796fb20d"
down_revision: Union[str, None] = "0358e660a680"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create deprecated_datasets table to store invalid datasets
    op.create_table(
        "deprecated_datasets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column("deprecated_on", sa.DateTime(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create deprecated_tags_datasets table
    op.create_table(
        "deprecated_tags_datasets",
        sa.Column("tag_id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("deprecated_on", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("tag_id", "dataset_id"),
    )

    # Create deprecated_data_products_datasets table
    op.create_table(
        "deprecated_data_products_datasets",
        sa.Column("data_product_id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("deprecated_on", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("data_product_id", "dataset_id"),
    )

    # Create deprecated_data_outputs_datasets table
    op.create_table(
        "deprecated_data_outputs_datasets",
        sa.Column("data_output_id", sa.Uuid(), nullable=False),
        sa.Column("dataset_id", sa.Uuid(), nullable=False),
        sa.Column("requested_on", sa.DateTime(), nullable=False),
        sa.Column("deprecated_on", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("data_output_id", "dataset_id"),
    )

    # Move datasets with multiple different owner_ids to deprecated_datasets
    op.execute(
        """
        INSERT INTO deprecated_datasets (id, name, description, created_on,
            updated_on, deprecated_on, reason)
        SELECT d.id, d.name, d.description, d.created_on, d.updated_on, NOW(),
          'multiple_data_product_owners'
        FROM datasets d
        WHERE d.id IN (
            SELECT dataset_id
            FROM data_outputs_datasets dod
            JOIN data_outputs dos ON dod.data_output_id = dos.id
            GROUP BY dataset_id
            HAVING COUNT(DISTINCT dos.owner_id) > 1
        )
        """
    )

    # Move datasets with no data outputs to deprecated_datasets
    op.execute(
        """
        INSERT INTO deprecated_datasets (id, name, description,
            created_on, updated_on, deprecated_on, reason)
        SELECT d.id, d.name, d.description, d.created_on, d.updated_on, NOW(),
            'no_data_outputs'
        FROM datasets d
        WHERE d.id NOT IN (
            SELECT DISTINCT dataset_id
            FROM data_outputs_datasets
            WHERE dataset_id IS NOT NULL
        )
        AND d.id NOT IN (
            SELECT id FROM deprecated_datasets
        )
        """
    )

    # Move related records from tags_datasets to deprecated table
    op.execute(
        """
        INSERT INTO deprecated_tags_datasets (tag_id, dataset_id, deprecated_on)
        SELECT td.tag_id, td.dataset_id, NOW()
        FROM tags_datasets td
        WHERE td.dataset_id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Move related records from data_products_datasets to deprecated table
    op.execute(
        """
        INSERT INTO deprecated_data_products_datasets (data_product_id,
            dataset_id, deprecated_on)
        SELECT dpd.data_product_id, dpd.dataset_id, NOW()
        FROM data_products_datasets dpd
        WHERE dpd.dataset_id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Move related records from data_outputs_datasets to deprecated table
    op.execute(
        """
        INSERT INTO deprecated_data_outputs_datasets (data_output_id,
            dataset_id, requested_on, deprecated_on)
        SELECT dod.data_output_id, dod.dataset_id, dod.requested_on, NOW()
        FROM data_outputs_datasets dod
        WHERE dod.dataset_id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Remove related records from tags_datasets before deleting datasets
    op.execute(
        """
        DELETE FROM tags_datasets
        WHERE dataset_id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Remove related records from data_products_datasets before deleting datasets
    op.execute(
        """
        DELETE FROM data_products_datasets
        WHERE dataset_id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Remove related records from data_outputs_datasets before deleting datasets
    op.execute(
        """
        DELETE FROM data_outputs_datasets
        WHERE dataset_id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Remove invalid datasets from datasets table
    op.execute(
        """
        DELETE FROM datasets
        WHERE id IN (SELECT id FROM deprecated_datasets)
        """
    )

    # Add data_product_id column to remaining datasets
    op.add_column("datasets", sa.Column("data_product_id", sa.Uuid(), nullable=True))

    # Set data_product_id for remaining valid datasets
    op.execute(
        """
        UPDATE datasets
        SET data_product_id = (
            SELECT dos.owner_id
            FROM data_outputs_datasets dod
            JOIN data_outputs dos ON dod.data_output_id = dos.id
            WHERE dod.dataset_id = datasets.id
            ORDER BY dod.requested_on ASC
            LIMIT 1
        )
        """
    )

    op.alter_column("datasets", "data_product_id", nullable=False)

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_datasets_data_product_id_data_products",
        "datasets",
        "data_products",
        ["data_product_id"],
        ["id"],
    )


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint(
        "fk_datasets_data_product_id_data_products", "datasets", type_="foreignkey"
    )

    # Make data_product_id nullable before restoring datasets
    op.alter_column("datasets", "data_product_id", nullable=True)

    # Restore deprecated datasets back to datasets table
    op.execute(
        """
        INSERT INTO datasets (id, name, description, created_on,
            updated_on, data_product_id)
        SELECT id, name, description, created_on, updated_on, NULL
        FROM deprecated_datasets
        """
    )

    # Restore tags_datasets relationships
    op.execute(
        """
        INSERT INTO tags_datasets (tag_id, dataset_id)
        SELECT tag_id, dataset_id
        FROM deprecated_tags_datasets
        """
    )

    # Restore data_products_datasets relationships
    op.execute(
        """
        INSERT INTO data_products_datasets (data_product_id, dataset_id)
        SELECT data_product_id, dataset_id
        FROM deprecated_data_products_datasets
        """
    )

    # Restore data_outputs_datasets relationships
    op.execute(
        """
        INSERT INTO data_outputs_datasets (data_output_id, dataset_id, requested_on)
        SELECT data_output_id, dataset_id, requested_on
        FROM deprecated_data_outputs_datasets
        """
    )

    # Drop data_product_id column
    op.drop_column("datasets", "data_product_id")

    # Drop deprecated tables
    op.drop_table("deprecated_data_outputs_datasets")
    op.drop_table("deprecated_data_products_datasets")
    op.drop_table("deprecated_tags_datasets")
    op.drop_table("deprecated_datasets")
