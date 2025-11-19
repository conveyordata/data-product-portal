"""grant API user admin

Revision ID: 6441623a586b
Revises: 7727032896e7
Create Date: 2025-05-21 10:55:00.964055

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.role_assignments.global_.router import (
    delete_assignment,
)
from app.roles import ADMIN_UUID
from app.users.model import User

# revision identifiers, used by Alembic.
revision: str = "6441623a586b"
down_revision: Union[str, None] = "7727032896e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())
    api_bot = session.execute(
        sa.select(User.id, User.email).filter_by(email="systemaccount@noreply.com")
    ).first()

    if api_bot:
        # Check if the user already has the role
        existing_assignments = (
            session.execute(
                sa.select(GlobalRoleAssignment).filter_by(user_id=api_bot.id)
            )
            .scalars()
            .all()
        )

        if not existing_assignments:
            sa.insert(GlobalRoleAssignment).values(
                user_id=api_bot.id,
                role_id=ADMIN_UUID,
                decision=DecisionStatus.APPROVED.value,
            )


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    api_bot = session.execute(
        sa.select(User.id, User.email).filter_by(email="systemaccount@noreply.com")
    ).first()

    if api_bot:
        # Check if the user has the admin role assignment
        existing_assignments = (
            session.execute(
                sa.select(GlobalRoleAssignment).filter_by(
                    user_id=api_bot.id, role_id=ADMIN_UUID
                )
            )
            .scalars()
            .all()
        )

        for assignment in existing_assignments:
            # Delete the role assignment
            delete_assignment(assignment.id, db=session, user=api_bot)

        session.commit()
