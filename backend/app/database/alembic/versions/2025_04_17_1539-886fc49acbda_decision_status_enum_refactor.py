"""Decision Status enum refactor

Revision ID: 886fc49acbda
Revises: 6fd335d0dcfe
Create Date: 2025-04-17 15:39:35.942198

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "886fc49acbda"
down_revision: Union[str, None] = "6fd335d0dcfe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute(
        "ALTER TYPE dataproductmembershipstatus "
        "RENAME VALUE 'PENDING_APPROVAL' TO 'PENDING';"
    )
    op.execute(
        "ALTER TYPE dataproductdatasetlinkstatus "
        "RENAME VALUE 'PENDING_APPROVAL' TO 'PENDING';"
    )
    op.execute(
        "ALTER TYPE dataoutputdatasetlinkstatus "
        "RENAME VALUE 'PENDING_APPROVAL' TO 'PENDING';"
    )

    for table, column in [
        ("data_product_memberships", "status"),
        ("data_products_datasets", "status"),
        ("data_outputs_datasets", "status"),
    ]:
        op.execute(
            f"""
            ALTER TABLE {table}
              ALTER COLUMN {column}
              TYPE decisionstatus
              USING {column}::text::decisionstatus;
        """
        )

    op.execute("DROP TYPE dataproductmembershipstatus;")
    op.execute("DROP TYPE dataproductdatasetlinkstatus;")
    op.execute("DROP TYPE dataoutputdatasetlinkstatus;")


def downgrade() -> None:

    op.execute(
        """
        CREATE TYPE dataproductmembershipstatus AS ENUM (
            'PENDING',
            'APPROVED',
            'DENIED'
        );
    """
    )
    op.execute(
        """
        CREATE TYPE dataproductdatasetlinkstatus AS ENUM (
            'PENDING',
            'APPROVED',
            'DENIED'
        );
    """
    )
    op.execute(
        """
        CREATE TYPE dataoutputdatasetlinkstatus AS ENUM (
            'PENDING',
            'APPROVED',
            'DENIED'
        );
    """
    )

    for table, column, enum_type in [
        ("data_product_memberships", "status", "dataproductmembershipstatus"),
        ("data_products_datasets", "status", "dataproductdatasetlinkstatus"),
        ("data_outputs_datasets", "status", "dataoutputdatasetlinkstatus"),
    ]:
        op.execute(
            f"""
            ALTER TABLE {table}
              ALTER COLUMN {column}
              TYPE {enum_type}
              USING {column}::text::{enum_type};
        """
        )

    op.execute(
        "ALTER TYPE dataproductmembershipstatus "
        "RENAME VALUE 'PENDING' TO 'PENDING_APPROVAL';"
    )
    op.execute(
        "ALTER TYPE dataproductdatasetlinkstatus "
        "RENAME VALUE 'PENDING' TO 'PENDING_APPROVAL';"
    )
    op.execute(
        "ALTER TYPE dataoutputdatasetlinkstatus "
        "RENAME VALUE 'PENDING' TO 'PENDING_APPROVAL';"
    )
