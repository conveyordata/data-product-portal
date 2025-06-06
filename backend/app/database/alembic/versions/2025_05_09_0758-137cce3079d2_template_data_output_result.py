"""template data output result

Revision ID: 137cce3079d2
Revises: eb57869c9840
Create Date: 2025-05-09 07:58:41.192102

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "137cce3079d2"
down_revision: Union[str, None] = "eb57869c9840"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("environments", sa.Column("acronym", sa.String, unique=True))
    op.add_column("platform_services", sa.Column("result_string_template", sa.String))
    op.add_column("platform_services", sa.Column("technical_info_template", sa.String))

    result_templates = {
        "S3": "{bucket}/{suffix}/{path}",
        "Glue": "{database}__{database_suffix}.{table}",
        "Snowflake": "{database}.{schema}.{table}",
        "Databricks": "{catalog}.{schema}.{table}",
        "Redshift": "{database}__{schema}.{table}",
    }

    technical_info_templates = {
        "S3": "{bucket_arn}/{bucket}/{suffix}/{path}/*",
        "Glue": "{database}__{database_suffix}.{table}",
        "Snowflake": "{database}.{schema}.{table}",
        "Databricks": "{catalog}.{schema}.{table}",
        "Redshift": "{database}__{schema}.{table}",
    }

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for service_name, result_template in result_templates.items():
        session.execute(
            sa.text(
                """
                UPDATE platform_services
                SET result_string_template=:result_template,
                    technical_info_template=:technical_info_template
                WHERE name=:name
                """
            ),
            {
                "name": service_name,
                "result_template": result_template,
                "technical_info_template": technical_info_templates[service_name],
            },
        )

    session.commit()


def downgrade() -> None:
    op.drop_column("environments", "acronym")
    op.drop_column("platform_services", "result_string_template")
    op.drop_column("platform_services", "technical_info_template")
