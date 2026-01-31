from collections.abc import Sequence

from pydantic import BaseModel

from app.pending_actions.schema import PendingAction


class PendingActionResponse(BaseModel):
    pending_actions: Sequence[PendingAction]
