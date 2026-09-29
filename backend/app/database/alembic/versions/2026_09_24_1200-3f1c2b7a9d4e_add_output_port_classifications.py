"""add output port classifications

Revision ID: 3f1c2b7a9d4e
Revises: 18fb80f18c7d
Create Date: 2026-09-24 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "3f1c2b7a9d4e"
down_revision: Union[str, None] = "18fb80f18c7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_classifications",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("access_function", sa.String(), nullable=False),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_output_port_classification_name"),
    )
    op.execute(
        """
        INSERT INTO output_port_classifications (id, name, description, access_function, created_on)
        VALUES
            (gen_random_uuid(), 'Unrestricted', 'Data that anyone in the organisation may use. Access requests are approved automatically.', 'UNRESTRICTED', NOW()),
            (gen_random_uuid(), 'Restricted', 'Data that requires owner approval before a Data Product can use it.', 'RESTRICTED', NOW()),
            (gen_random_uuid(), 'Private', 'Data that is hidden from the rest of the organisation. Access requires owner approval.', 'PRIVATE', NOW())
        """
    )
    op.add_column("datasets", sa.Column("classification_id", sa.UUID(), nullable=True))
    op.alter_column("datasets", "access_type", new_column_name="access_function")
    op.execute(
        "UPDATE datasets SET access_function = 'UNRESTRICTED' WHERE access_function IS NULL"
    )
    op.alter_column("datasets", "access_function", nullable=False)
    op.execute(
        """
        UPDATE datasets SET classification_id = c.id
        FROM output_port_classifications c
        WHERE c.access_function = datasets.access_function
        """
    )
    op.alter_column("datasets", "classification_id", nullable=False)
    op.create_foreign_key(
        "datasets_classification_id_fkey",
        "datasets",
        "output_port_classifications",
        ["classification_id"],
        ["id"],
    )
    op.create_index("ix_datasets_classification_id", "datasets", ["classification_id"])


def downgrade() -> None:
    op.drop_constraint(
        "datasets_classification_id_fkey", "datasets", type_="foreignkey"
    )
    op.drop_column("datasets", "classification_id")
    op.alter_column(
        "datasets", "access_function", new_column_name="access_type", nullable=True
    )
    op.drop_table("output_port_classifications")
