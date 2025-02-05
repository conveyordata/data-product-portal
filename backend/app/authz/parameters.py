from typing import Annotated
from uuid import UUID

from fastapi import Depends
from typing_extensions import Optional


class AuthorizationParams:
    def __init__(self, object_id: Optional[UUID] = None, domain: Optional[str] = None):
        self.object_id: str = str(object_id) if object_id else "*"
        self.domain: str = domain if domain is not None else "*"


AuthorizationDep = Annotated[AuthorizationParams, Depends(AuthorizationParams)]
