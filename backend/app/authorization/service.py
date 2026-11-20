from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.authz import Authorization
from app.core.authz.actions import AuthorizationAction
from app.core.authz.resolvers import output_port_parent


class AuthorizationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def check_access(
        self,
        *,
        user_id: UUID,
        action: AuthorizationAction,
        resource: Optional[UUID],
        domain: Optional[UUID],
    ) -> bool:
        dom = "*" if domain is None else str(domain)
        obj = "*" if resource is None else str(resource)
        parent = output_port_parent(self.db, obj) if action.targets_output_port else "*"
        return Authorization(self.db).has_access(
            sub=str(user_id),
            dom=dom,
            obj=obj,
            parent=parent,
            act=action,
        )
