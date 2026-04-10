"""Extend platform services supported

Revision ID: 3a883d3ec0f6
Revises: 9621a226da7c
Create Date: 2026-04-09 13:07:46.384625

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlalchemy.orm as orm
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3a883d3ec0f6"
down_revision: Union[str, None] = "9621a226da7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    session.execute(
        sa.text(
            """
            UPDATE platform_services
            SET technical_info_template = '{bucket_arn}/{suffix}/{path}/*'
            WHERE name = 'S3'
            """
        )
    )

    azure_id = session.execute(
        sa.text(
            """
            INSERT INTO platforms (name) VALUES ('Azure')
            RETURNING id
            """
        )
    ).scalar_one()

    session.execute(
        sa.text(
            """
            INSERT INTO platform_services (name, platform_id, result_string_template, technical_info_template)
            VALUES ('azureblob', :platform_id, :result_template, :technical_info_template)
            """
        ),
        {
            "platform_id": azure_id,
            "result_template": "platform_provided_storage_account/{container_name}/{path}",
            "technical_info_template": "https://{storage_account}.blob.core.windows.net/{container_name}/{path}",
        },
    )

    op.drop_constraint(
        "platform_service_configs_service_id_fkey",
        "platform_service_configs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "platform_service_configs_service_id_fkey",
        "platform_service_configs",
        "platform_services",
        ["service_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "platform_service_configs_platform_id_fkey",
        "platform_service_configs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "platform_service_configs_platform_id_fkey",
        "platform_service_configs",
        "platforms",
        ["platform_id"],
        ["id"],
        ondelete="CASCADE",
    )

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.execute(
        sa.text(
            """
            DELETE FROM platform_services WHERE name = 'azureblob'
            """
        )
    )
    session.execute(
        sa.text(
            """
            DELETE
            FROM platforms
            WHERE name = 'Azure'
            """
        )
    )

    op.drop_constraint(
        "platform_service_configs_platform_id_fkey",
        "platform_service_configs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "platform_service_configs_platform_id_fkey",
        "platform_service_configs",
        "platforms",
        ["platform_id"],
        ["id"],
    )

    op.drop_constraint(
        "platform_service_configs_service_id_fkey",
        "platform_service_configs",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "platform_service_configs_service_id_fkey",
        "platform_service_configs",
        "platform_services",
        ["service_id"],
        ["id"],
    )
