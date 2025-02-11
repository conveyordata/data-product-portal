from uuid import UUID

from sqlalchemy.orm import Session

from app.database.database import ensure_exists
from app.roles.model import Role as RoleModel
from app.roles.schema import CreateRole, Role


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_role(self, id: UUID) -> RoleModel:
        return ensure_exists(id, self.db, Role)

    def get_roles(self, scope: str) -> list[Role]:
        return self.db.query(RoleModel).where(RoleModel.scope == scope).all()

    def create_role(self, role: CreateRole) -> Role:
        model = RoleModel(**role.parse_pydantic_schema())
        self.db.add(model)
        self.db.commit()
        return model

    def update_role(self, role: Role) -> Role:
        model = RoleModel(**role.parse_pydantic_schema())
        self.db.add(model)
        self.db.commit()
        return model

    def delete_role(self, id: UUID) -> None:
        role = self.get_role(id)
        role.delete()
        self.db.commit()
