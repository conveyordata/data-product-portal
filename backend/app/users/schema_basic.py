from uuid import UUID

from pydantic import EmailStr

from app.shared.schema import ORMModel


class UserBasic(ORMModel):
    id: UUID
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    is_admin: bool
