"""add embeddings

Revision ID: bc4327c7c467
Revises: b3f7df8cf884
Create Date: 2025-12-15 10:12:26.952993

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bc4327c7c467"
down_revision: Union[str, None] = "b3f7df8cf884"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("""
CREATE TABLE dataset_embeddings (
    id UUID PRIMARY KEY,
    embeddings vector(384)
)""")
    # op.create_table(
    #     "dataset_embeddings",
    #     sa.Column(
    #         "id",
    #         sa.UUID,
    #         primary_key=True,
    #         nullable=False,
    #     ),
    #     sa.Column(
    #         "embeddings",
    #         Vector(1024),
    #         nullable=True
    #     ),
    # )


def downgrade() -> None:
    op.drop_table("dataset_embeddings")
