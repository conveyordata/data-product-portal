from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import ensure_exists
from app.roles.model import Role as RoleModel
from app.roles.schema import CreateRole, Role, UpdateRole


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, role_id: UUID) -> RoleModel:
        return ensure_exists(role_id, self.db, RoleModel)

    def get_roles(self, scope: str) -> list[Role]:
        result = self.db.execute(
            select(RoleModel)
            .where(RoleModel.scope == scope)
            .order_by(RoleModel.created_on)
        )
        return [row.Role for row in result]

    def create_role(self, role: CreateRole) -> Role:
        model = RoleModel(**role.parse_pydantic_schema())
        model.permissions = self._canonical_permissions(model.permissions)
        self.db.add(model)
        self.db.commit()
        return model

    def update_role(self, role: UpdateRole) -> Role:
        db_role = self.get_role(role.id)
        updated_role = role.model_dump(exclude_unset=True)

        for k, v in updated_role.items():
            if k == "permissions":
                v = self._canonical_permissions(v)
            setattr(db_role, k, v) if v else None

        self.db.commit()
        return db_role

    def delete_role(self, id_: UUID) -> Role:
        role = self.get_role(id_)
        self.db.delete(role)
        self.db.commit()
        return role

    @staticmethod
    def _canonical_permissions(permissions: list[int]) -> list[int]:
        result = list(set(permissions))
        result.sort()
        return result
