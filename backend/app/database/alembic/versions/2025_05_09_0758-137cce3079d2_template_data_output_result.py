"""template data output result

Revision ID: 137cce3079d2
Revises: 7727032896e7
Create Date: 2025-05-09 07:58:41.192102

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "137cce3079d2"
down_revision: Union[str, None] = "7727032896e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("platform_services", sa.Column("template", sa.String))

    service_templates = {
        "S3": "{bucket}/{suffix}/{path}",
        "Glue": "{database}__{database_suffix}.{table}",
        "Snowflake": "{database}.{schema}.{table}",
        "Databricks": "{catalog}.{schema}.{table}",
        "Redshift": "{database}__{schema}.{table}",
    }

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for service_name, template in service_templates.items():
        session.execute(
            sa.text("UPDATE platform_services SET template=:template WHERE name=:name"),
            {"template": template, "name": service_name},
        )

    session.commit()


def downgrade() -> None:
    op.drop_column("platform_services", "template")
