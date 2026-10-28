"""add identity event reference entity

Revision ID: 4b6d2a8f1c35
Revises: a9203b7e41cd
Create Date: 2026-10-28 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "4b6d2a8f1c35"
down_revision: Union[str, None] = "a9203b7e41cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(
        sa.table("event_reference_entities", sa.column("key", sa.String)),
        [{"key": "IDENTITY"}],
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM events
                WHERE subject_type = 'IDENTITY'
                  AND subject_id NOT IN (SELECT id FROM users)
            ) OR EXISTS (
                SELECT 1
                FROM events
                WHERE target_type = 'IDENTITY'
                  AND target_id NOT IN (SELECT id FROM users)
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade while non-user identity events exist';
            END IF;
        END
        $$;
        """
    )
    op.execute("UPDATE events SET subject_type = 'USER' WHERE subject_type = 'IDENTITY'")
    op.execute("UPDATE events SET target_type = 'USER' WHERE target_type = 'IDENTITY'")
    op.execute("DELETE FROM event_reference_entities WHERE key = 'IDENTITY'")
