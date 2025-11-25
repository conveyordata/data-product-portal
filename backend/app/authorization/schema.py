from typing import Optional

from pydantic import BaseModel


class AccessResponse(BaseModel):
    allowed: bool


class IsAdminResponse(BaseModel):
    is_admin: bool
    time: Optional[str] = None
