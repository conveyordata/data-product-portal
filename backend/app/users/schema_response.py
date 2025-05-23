from uuid import UUID

from pydantic import EmailStr

from app.shared.schema import ORMModel


class BaseUserGet(ORMModel):
    id: UUID
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    is_admin: bool


class UserGet(BaseUserGet):
    pass


class UsersGet(BaseUserGet):
    pass
