from uuid import UUID

from app.events.schema import Event
from app.shared.schema import ORMModel
from app.users.schema import User


class Notification(ORMModel):
    id: UUID
    event_id: UUID
    event: Event
    user_id: UUID
    user: User
