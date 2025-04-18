from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.pending_actions.schema import PendingAction
from app.pending_actions.service import PendingActionService
from app.users.model import User

router = APIRouter(prefix="/pending_actions", tags=["pending_actions"])


@router.get("")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> list[PendingAction]:
    return PendingActionService().get_user_pending_actions(db, authenticated_user)
