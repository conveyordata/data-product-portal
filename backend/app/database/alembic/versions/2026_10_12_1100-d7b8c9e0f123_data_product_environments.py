"""Persist Data Product environment scope."""

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

revision = "d7b8c9e0f123"
down_revision = "b71a5f3e29cd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_product_environments",
        sa.Column(
            "data_product_id",
            sa.UUID(),
            sa.ForeignKey("data_products.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "environment_id",
            sa.UUID(),
            sa.ForeignKey("environments.id"),
            primary_key=True,
        ),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=False),
            nullable=False,
            server_default=utcnow(),
        ),
    )
    op.execute(
        sa.text("""
        INSERT INTO data_product_environments (data_product_id, environment_id, creation_date)
        SELECT dp.id, de.environment_id, COALESCE(de.created_on, TIMEZONE('utc', CURRENT_TIMESTAMP))
        FROM data_products dp
        JOIN abstract_data_products adp ON adp.id = dp.id
        JOIN domain_environments de ON de.domain_id = adp.domain_id
        UNION ALL
        SELECT dp.id, env.id, TIMEZONE('utc', CURRENT_TIMESTAMP)
        FROM data_products dp
        JOIN abstract_data_products adp ON adp.id = dp.id
        CROSS JOIN environments env
        WHERE env.is_global = TRUE
          AND NOT EXISTS (SELECT 1 FROM domain_environments de WHERE de.domain_id = adp.domain_id)
    """)
    )
    missing_environments = op.get_bind().scalar(
        sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM data_products dp
            WHERE NOT EXISTS (
                SELECT 1 FROM data_product_environments dpe WHERE dpe.data_product_id = dp.id
            )
        )
    """)
    )
    if missing_environments:
        raise RuntimeError(
            "Configure global or Domain environments before migrating Data Products"
        )


def downgrade() -> None:
    op.drop_table("data_product_environments")
