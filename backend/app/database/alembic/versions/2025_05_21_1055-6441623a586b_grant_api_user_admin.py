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
    create_assignment,
    decide_assignment,
    delete_assignment,
)
from app.role_assignments.global_.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
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
    api_bot = session.scalar(
        sa.select(User).filter_by(email="systemaccount@noreply.com")
    )

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
            # Assign the role to the user
            assignment = create_assignment(
                request=CreateRoleAssignment(
                    user_id=api_bot.id,
                    role_id=ADMIN_UUID,
                ),
                db=session,
                user=api_bot,
            )
            decide_assignment(
                id=assignment.id,
                request=DecideRoleAssignment(decision=DecisionStatus.APPROVED),
                db=session,
                user=api_bot,
            )


def downgrade() -> None:
    session = Session(bind=op.get_bind())
    api_bot = session.scalar(
        sa.select(User).filter_by(email="systemaccount@noreply.com")
    )

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
