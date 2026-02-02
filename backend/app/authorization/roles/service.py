from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.authorization.roles import ADMIN_UUID
from app.authorization.roles.model import Role as RoleModel
from app.authorization.roles.schema import (
    CreateRole,
    Prototype,
    Role,
    Scope,
    UpdateRole,
)
from app.core.authz import Action
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

    def initialize_prototype_roles(self) -> bool:
        """Initializes the roles that are expected to be present in other parts of the
        application. This function will first check which roles are already present,
        and only create the missing ones.

        Returns: True if a role was added, False otherwise.
        """
        modified = False

        if self.find_prototype(Scope.GLOBAL, Prototype.ADMIN) is None:
            modified = True
            model = RoleModel(
                id=ADMIN_UUID,
                scope=Scope.GLOBAL,
                prototype=Prototype.ADMIN,
                name="Admin",
                description="Administrators have blanket permissions",
                permissions=[],
            )
            self.db.add(model)
            self.db.commit()

        if self.find_prototype(Scope.GLOBAL, Prototype.EVERYONE) is None:
            modified = True
            self.create_role(
                CreateRole(
                    name="everyone",
                    scope=Scope.GLOBAL,
                    description="This is the role that is used as fallback for users that don't have another role",  # noqa: E501
                    permissions=[
                        Action.GLOBAL__CREATE_DATAPRODUCT,
                        Action.GLOBAL__CREATE_OUTPUT_PORT,
                        Action.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
                        Action.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS,
                    ],
                ),
                prototype=Prototype.EVERYONE,
            )

        if self.find_prototype(Scope.DATASET, Prototype.OWNER) is None:
            modified = True
            self.create_role(
                CreateRole(
                    name="owner",
                    scope=Scope.DATASET,
                    description="The owner of a Dataset",
                    permissions=[
                        Action.OUTPUT_PORT__UPDATE_PROPERTIES,
                        Action.OUTPUT_PORT__UPDATE_SETTINGS,
                        Action.OUTPUT_PORT__UPDATE_STATUS,
                        Action.OUTPUT_PORT__DELETE,
                        Action.OUTPUT_PORT__CREATE_USER,
                        Action.OUTPUT_PORT__UPDATE_USER,
                        Action.OUTPUT_PORT__DELETE_USER,
                        Action.OUTPUT_PORT__APPROVE_USER_REQUEST,
                        Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
                        Action.OUTPUT_PORT__REVOKE_TECHNICAL_ASSET_LINK,
                        Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                        Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
                        Action.OUTPUT_PORT__READ_INTEGRATIONS,
                        Action.OUTPUT_PORT__UPDATE_DATA_QUALITY,
                    ],
                ),
                prototype=Prototype.OWNER,
            )

        if self.find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER) is None:
            modified = True
            self.create_role(
                CreateRole(
                    name="owner",
                    scope=Scope.DATA_PRODUCT,
                    description="The owner of a Data Product",
                    permissions=[
                        Action.DATA_PRODUCT__UPDATE_PROPERTIES,
                        Action.DATA_PRODUCT__UPDATE_SETTINGS,
                        Action.DATA_PRODUCT__UPDATE_STATUS,
                        Action.DATA_PRODUCT__DELETE,
                        Action.DATA_PRODUCT__CREATE_USER,
                        Action.DATA_PRODUCT__UPDATE_USER,
                        Action.DATA_PRODUCT__DELETE_USER,
                        Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
                        Action.DATA_PRODUCT__CREATE_TECHNICAL_ASSET,
                        Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET,
                        Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET,
                        Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK,
                        Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                        Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
                        Action.DATA_PRODUCT__READ_INTEGRATIONS,
                    ],
                ),
                prototype=Prototype.OWNER,
            )

        return modified

    def find_prototype(self, scope: Scope, prototype: Prototype) -> Optional[Role]:
        return self.db.scalars(
            select(RoleModel)
            .where(RoleModel.scope == scope)
            .where(RoleModel.prototype == prototype)
        ).one_or_none()
