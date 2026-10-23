"""Remove legacy Domain environment declarations."""

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

revision = "a82c9b3e7d41"
down_revision = "d7b8c9e0f123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    products = sa.table("data_products", sa.column("id", sa.UUID()))
    declarations = sa.table(
        "data_product_environments", sa.column("data_product_id", sa.UUID())
    )
    missing = op.get_bind().scalar(
        sa.select(products.c.id)
        .where(~sa.exists().where(declarations.c.data_product_id == products.c.id))
        .limit(1)
    )
    if missing is not None:
        raise RuntimeError(
            "Declare environments for every Data Product before removing Domain environments"
        )
    op.drop_table("domain_environments")


def downgrade() -> None:
    op.create_table(
        "domain_environments",
        sa.Column(
            "domain_id",
            sa.UUID(),
            sa.ForeignKey("domains.id"),
            primary_key=True,
            index=True,
        ),
        sa.Column(
            "environment_id",
            sa.UUID(),
            sa.ForeignKey("environments.id"),
            primary_key=True,
            index=True,
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
