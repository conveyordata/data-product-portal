"""Add explorations

Revision ID: d6286ec9911b
Revises: 3a883d3ec0f6
Create Date: 2026-04-17 15:05:20.883326

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "d6286ec9911b"
down_revision: Union[str, None] = "c8a49838fa13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "abstract_data_products",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("abstract_data_product_type", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("namespace", sa.String(), nullable=False),
        sa.Column(
            "domain_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("domains.id"),
            nullable=False,
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )

    op.execute(
        """
        INSERT INTO abstract_data_products (
            id,
            name,
            abstract_data_product_type,
            description,
            domain_id,
            namespace,
            created_on,
            updated_on,
            deleted_at
        )
        SELECT
            id,
            name,
            'data_products',
            description,
            domain_id,
            namespace,
            created_on,
            updated_on,
            deleted_at
        FROM data_products
        """
    )

    op.create_foreign_key(
        "data_products_id_fkey",
        "data_products",
        "abstract_data_products",
        ["id"],
        ["id"],
    )

    op.create_table(
        "explorations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("abstract_data_products.id"),
            primary_key=True,
            nullable=False,
        ),
    )

    op.execute(
        "ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_data_product_name"
    )
    op.execute(
        "ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_data_product_namespace"
    )
    op.create_unique_constraint(
        "uq_abstract_data_products_name",
        "abstract_data_products",
        ["name"],
        postgresql_nulls_not_distinct=True,
    )
    op.create_unique_constraint(
        "uq_abstract_data_products_namespace",
        "abstract_data_products",
        ["namespace"],
        postgresql_nulls_not_distinct=True,
    )

    op.drop_column("data_products", "name")
    op.drop_column("data_products", "description")
    op.drop_column("data_products", "domain_id")
    op.drop_column("data_products", "namespace")
    op.drop_column("data_products", "created_on")
    op.drop_column("data_products", "updated_on")
    op.drop_column("data_products", "deleted_at")


def downgrade() -> None:
    op.add_column(
        "data_products",
        sa.Column("name", sa.String(), nullable=True),
    )
    op.add_column(
        "data_products",
        sa.Column("namespace", sa.String(), nullable=True),
    )
    op.add_column(
        "data_products",
        sa.Column("description", sa.String(), nullable=True),
    )
    op.add_column(
        "data_products",
        sa.Column("domain_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "data_products",
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
    )
    op.add_column(
        "data_products",
        sa.Column("updated_on", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "data_products",
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )

    op.execute(
        """
        UPDATE data_products AS dp
        SET
            name = adp.name,
            description = adp.description,
            namespace = adp.namespace,
            domain_id = adp.domain_id,
            created_on = adp.created_on,
            updated_on = adp.updated_on,
            deleted_at = adp.deleted_at
        FROM abstract_data_products AS adp
        WHERE dp.id = adp.id
        """
    )

    op.create_foreign_key(
        "data_products_domain_id_fkey",
        "data_products",
        "domains",
        ["domain_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_data_product_name",
        "data_products",
        ["name"],
        postgresql_nulls_not_distinct=True,
    )
    op.create_unique_constraint(
        "uq_data_product_namespace",
        "data_products",
        ["namespace"],
        postgresql_nulls_not_distinct=True,
    )
    op.execute(
        "ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_abstract_data_products_name"
    )
    op.execute(
        "ALTER TABLE data_products DROP CONSTRAINT IF EXISTS uq_abstract_data_products_namespace"
    )

    op.drop_table("explorations")
    op.drop_constraint("data_products_id_fkey", "data_products", type_="foreignkey")
    op.drop_table("abstract_data_products")
