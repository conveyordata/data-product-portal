from pydantic import BaseModel


class AccessResponse(BaseModel):
    allowed: bool
