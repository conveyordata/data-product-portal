from typing import Annotated
from uuid import UUID

from fastapi import Depends
from typing_extensions import Optional


class AuthorizationParams:
    def __init__(self, object_id: UUID, domain: Optional[str] = None):
        self.object_id: UUID = object_id
        self.domain: str = domain if domain is not None else "*"


AuthorizationDep = Annotated[AuthorizationParams, Depends(AuthorizationParams)]
