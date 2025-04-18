from sqlalchemy.orm import Session

from app.pending_actions.schema import (
    PendingAction,
)
from app.users.schema import User


class PendingActionService:

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> list[PendingAction]:
        return
