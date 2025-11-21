from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr

from app.shared.schema import ORMModel


class User(ORMModel):
    id: UUID
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    has_seen_tour: bool
    can_become_admin: bool
    admin_expiry: Optional[datetime] = None
