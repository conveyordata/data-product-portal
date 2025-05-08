from pydantic import EmailStr

from app.shared.schema import ORMModel


class UserCreate(ORMModel):
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    is_admin: bool = False
