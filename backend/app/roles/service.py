from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.authz.actions import AuthorizationAction
from app.database.database import ensure_exists
from app.roles.model import Role as RoleModel
from app.roles.schema import CreateRole, Prototype, Role, Scope, UpdateRole

ADMIN_UUID = UUID(int=0)


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

    def update_role(self, request: UpdateRole) -> Role:
        role = self.get_role(request.id)
        update = request.model_dump(exclude_unset=True)

        if (
            Scope(role.scope) is Scope.GLOBAL
            and Prototype(role.prototype) is Prototype.ADMIN
            and "permissions" in update.keys()
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="You cannot change the permissions of the admin role",
            )

        for k, v in update.items():
            if k == "permissions":
                v = self._canonical_permissions(v)
            setattr(role, k, v) if v else None

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

    def initialize_prototype_roles(self) -> None:
        """Initializes the roles that are expected to be present in other parts of the
        application. This function will first check which roles are already present,
        and only create the missing ones.
        """

        if self.find_prototype(Scope.GLOBAL, Prototype.ADMIN) is None:
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
            self.create_role(
                CreateRole(
                    name="everyone",
                    scope=Scope.GLOBAL,
                    description="This is the role that is used as fallback for users that don't have another role",  # noqa: E501
                    permissions=[
                        AuthorizationAction.GLOBAL__CREATE_DATAPRODUCT,
                        AuthorizationAction.GLOBAL__CREATE_DATASET,
                        AuthorizationAction.GLOBAL__REQUEST_DATAPRODUCT_ACCESS,
                        AuthorizationAction.GLOBAL__REQUEST_DATASET_ACCESS,
                    ],
                ),
                prototype=Prototype.EVERYONE,
            )

        if self.find_prototype(Scope.DATASET, Prototype.OWNER) is None:
            self.create_role(
                CreateRole(
                    name="owner",
                    scope=Scope.DATASET,
                    description="The owner of a Dataset",
                    permissions=[
                        AuthorizationAction.DATASET__UPDATE_PROPERTIES,
                        AuthorizationAction.DATASET__UPDATE_SETTINGS,
                        AuthorizationAction.DATASET__UPDATE_STATUS,
                        AuthorizationAction.DATASET__DELETE,
                        AuthorizationAction.DATASET__CREATE_USER,
                        AuthorizationAction.DATASET__UPDATE_USER,
                        AuthorizationAction.DATASET__DELETE_USER,
                        AuthorizationAction.DATASET__APPROVE_USER_REQUEST,
                        AuthorizationAction.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                        AuthorizationAction.DATASET__REVOKE_DATA_OUTPUT_LINK,
                        AuthorizationAction.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                        AuthorizationAction.DATASET__REVOKE_DATAPRODUCT_ACCESS,
                        AuthorizationAction.DATASET__READ_INTEGRATIONS,
                    ],
                ),
                prototype=Prototype.OWNER,
            )

        if self.find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER) is None:
            self.create_role(
                CreateRole(
                    name="owner",
                    scope=Scope.DATA_PRODUCT,
                    description="The owner of a Data Product",
                    permissions=[
                        AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
                        AuthorizationAction.DATA_PRODUCT__UPDATE_SETTINGS,
                        AuthorizationAction.DATA_PRODUCT__UPDATE_STATUS,
                        AuthorizationAction.DATA_PRODUCT__DELETE,
                        AuthorizationAction.DATA_PRODUCT__CREATE_USER,
                        AuthorizationAction.DATA_PRODUCT__UPDATE_USER,
                        AuthorizationAction.DATA_PRODUCT__DELETE_USER,
                        AuthorizationAction.DATA_PRODUCT__APPROVE_USER_REQUEST,
                        AuthorizationAction.DATA_PRODUCT__CREATE_DATA_OUTPUT,
                        AuthorizationAction.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                        AuthorizationAction.DATA_PRODUCT__DELETE_DATA_OUTPUT,
                        AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                        AuthorizationAction.DATA_PRODUCT__REQUEST_DATASET_ACCESS,
                        AuthorizationAction.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
                        AuthorizationAction.DATA_PRODUCT__READ_INTEGRATIONS,
                    ],
                ),
                prototype=Prototype.OWNER,
            )

    def find_prototype(self, scope: Scope, prototype: Prototype) -> Optional[Role]:
        return self.db.scalars(
            select(RoleModel)
            .where(RoleModel.scope == scope)
            .where(RoleModel.prototype == prototype)
        ).one_or_none()
