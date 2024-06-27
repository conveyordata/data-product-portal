from pydantic import EmailStr
from app.shared.schema import ORMModel
from uuid import UUID


class UserCreate(ORMModel):
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str


class User(UserCreate):
    id: UUID
