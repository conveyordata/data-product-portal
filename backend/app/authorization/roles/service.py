from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.roles.model import Role as RoleModel
from app.authorization.roles.schema import (
    CreateRole,
    Prototype,
    Role,
    Scope,
    UpdateRole,
)
from app.database.database import ensure_exists


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, role_id: UUID) -> RoleModel:
        return ensure_exists(role_id, self.db, RoleModel)

    def get_roles(self, scope: Optional[Scope] = None) -> Sequence[Role]:
        query = select(RoleModel)
        if scope:
            query = query.where(RoleModel.scope == scope)
        return self.db.scalars(query.order_by(RoleModel.created_on)).all()

    def create_role(
        self, role: CreateRole, *, prototype: Prototype = Prototype.CUSTOM
    ) -> Role:
        model = RoleModel(**role.parse_pydantic_schema())
        model.prototype = prototype
        model.permissions = self._canonical_permissions(model.permissions)
        self.db.add(model)
        self.db.commit()
        return model

    def update_role(self, id: UUID, request: UpdateRole) -> Role:
        role = self.get_role(id)
        update = request.model_dump(exclude_unset=True)

        if (
            Scope(role.scope) is Scope.GLOBAL
            and Prototype(role.prototype) is Prototype.ADMIN
            and "permissions" in update
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You cannot change the permissions of the admin role",
            )
        for k, v in update.items():
            if k == "permissions":
                v = self._canonical_permissions(v)
            setattr(role, k, v)

        self.db.commit()
        return role

    def delete_role(self, id_: UUID) -> Role:
        role = self.get_role(id_)
        if role.prototype != Prototype.CUSTOM:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This role cannot be deleted",
            )

        self.db.delete(role)
        self.db.commit()
        return role

    @staticmethod
    def _canonical_permissions(permissions: list[int]) -> list[int]:
        result = list(set(permissions))
        result.sort()
        return result

    def find_prototype(self, scope: Scope, prototype: Prototype) -> Role:
        return self.db.scalars(
            select(RoleModel)
            .where(RoleModel.scope == scope)
            .where(RoleModel.prototype == prototype)
        ).one()
