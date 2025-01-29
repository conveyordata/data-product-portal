"""empty message

Revision ID: 4c49c19ee972
Revises: ca11eb0735ed, 0402aaf51be7
Create Date: 2025-01-23 11:17:39.198274

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "4c49c19ee972"
down_revision: Union[tuple[str, str], None] = ("ca11eb0735ed", "0402aaf51be7")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
