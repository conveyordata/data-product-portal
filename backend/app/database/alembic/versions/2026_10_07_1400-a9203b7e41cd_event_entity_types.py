from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9203b7e41cd"
down_revision: Union[str, None] = "3f1c2b7a9d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _rename_entities({"DATASET": "OUTPUT_PORT", "DATA_OUTPUT": "TECHNICAL_ASSET"})


def downgrade() -> None:
    _rename_entities({"OUTPUT_PORT": "DATASET", "TECHNICAL_ASSET": "DATA_OUTPUT"})


def _rename_entities(renames: dict[str, str]) -> None:
    entities = sa.table("event_reference_entities", sa.column("key", sa.String))
    events = sa.table(
        "events",
        sa.column("subject_type", sa.String),
        sa.column("target_type", sa.String),
    )
    op.bulk_insert(entities, [{"key": name} for name in renames.values()])
    for old_name, new_name in renames.items():
        op.execute(
            events.update()
            .where(events.c.subject_type == old_name)
            .values(subject_type=new_name)
        )
        op.execute(
            events.update()
            .where(events.c.target_type == old_name)
            .values(target_type=new_name)
        )
    op.execute(entities.delete().where(entities.c.key.in_(renames)))
