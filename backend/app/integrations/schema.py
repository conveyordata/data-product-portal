from pydantic import BaseModel
from uuid import UUID

class Integration(BaseModel):
    uuid: UUID
    integration_type: str
    url: str

    class Config:
        orm_mode = True
