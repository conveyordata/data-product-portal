"""add data_product_id to dataset

Revision ID: 249eae21bcac
Revises: d56d796fb20d
Create Date: 2025-10-29 10:32:01.866274

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "249eae21bcac"
down_revision: Union[str, None] = "f0b94d78c72c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("datasets", sa.Column("search_vector", postgresql.TSVECTOR))

    op.create_index(
        "idx_datasets_search_vector",
        "datasets",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )

    op.execute(
        """
WITH data_outputs_vectors AS (
    SELECT
       dod.dataset_id,
       (
            setweight(to_tsvector('english',
                      string_agg(coalesce(data_outputs.name, ''), ' ')),
                      'A') ||
            setweight(to_tsvector('english',
                      string_agg(coalesce(data_outputs.description, ''), ' ')),
                      'B')
        ) AS search_vector
    FROM data_outputs
    JOIN data_outputs_datasets dod on dod.data_output_id = data_outputs.id
    GROUP BY dod.dataset_id
),
dataset_search_vectors AS (
    SELECT
        datasets.id,
        (
            setweight(to_tsvector('english', coalesce(datasets.name, '')),
                      'A') ||
            setweight(to_tsvector('english', coalesce(datasets.description, '')),
                      'B') ||
            coalesce(dov.search_vector, to_tsvector('english', ''))
        ) AS new_search_vector
    FROM datasets
    LEFT JOIN data_outputs_vectors dov ON dov.dataset_id = datasets.id
)
UPDATE datasets ds
SET search_vector = csv.new_search_vector
FROM dataset_search_vectors csv
WHERE ds.id = csv.id;
    """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_datasets_search_vector;")
    op.drop_column("datasets", "search_vector")
