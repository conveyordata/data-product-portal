"""revamp data output columns

Revision ID: ca11eb0735ed
Revises: 6516756ada04
Create Date: 2024-12-02 13:51:07.924946

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ca11eb0735ed"
down_revision: Union[str, None] = "6516756ada04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_output_configurations", sa.Column("catalog", sa.String))
    op.add_column("data_output_configurations", sa.Column("catalog_path", sa.String))
    op.execute(
        """UPDATE public.data_output_configurations
SET catalog=schema, catalog_path=schema_path, schema=schema_suffix,
 schema_suffix=NULL, schema_path=NULL
WHERE configuration_type = 'DatabricksDataOutput';"""
    )
    op.execute(
        """UPDATE public.data_output_configurations
SET database=schema, schema=schema_suffix, schema_suffix=NULL,
database_path=schema_path, schema_path=NULL
WHERE configuration_type = 'SnowflakeDataOutput';"""
    )


def downgrade() -> None:
    op.execute(
        """UPDATE public.data_output_configurations
SET schema_path=catalog_path, schema_suffix=schema, schema=catalog
WHERE configuration_type = 'DatabricksDataOutput';"""
    )
    op.execute(
        """UPDATE public.data_output_configurations
SET schema_suffix=schema, schema=database, database=NULL,
 schema_path=database_path, database_path=NULL
WHERE configuration_type = 'SnowflakeDataOutput';"""
    )
    op.drop_column("data_output_configurations", "catalog")
    op.drop_column("data_output_configurations", "catalog_path")
