from abc import ABC
from collections.abc import Callable
from pathlib import Path
from typing import Sequence, Type, TypeAlias, Union, cast

import casbin_async_sqlalchemy_adapter as sqlalchemy_adapter
from cachetools import Cache, LRUCache, cachedmethod
from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.data_outputs.model import DataOutput
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.model import DataProductMembership
from app.data_products.model import DataProduct
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database import database
from app.database.database import get_db_session
from app.datasets.model import Dataset
from app.settings import settings
from app.users.schema import User
from app.utils.singleton import Singleton

from .actions import AuthorizationAction

Model: TypeAlias = Union[Type[DataProduct], Type[Dataset], Type[DataOutput], None]


class SubjectResolver(ABC):
    DEFAULT: str = "*"
    model: Model = None

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        if (result := request.query_params.get(key)) is not None:
            return cast(str, result)
        if (result := request.path_params.get(key)) is not None:
            return cast(str, result)
        return cls.DEFAULT

    @classmethod
    def resolve_domain(
        cls,
        db: Session,
        id_: str,
    ) -> str:
        if id_ == cls.DEFAULT or cls.model is None:
            return cls.DEFAULT
        domain = db.scalars(
            select(cls.model.domain_id).where(cls.model.id == id_)
        ).one_or_none()
        return cls.DEFAULT if domain is None else str(domain)


class DataProductResolver(SubjectResolver):
    model: Model = DataProduct


class DatasetResolver(SubjectResolver):
    model: Model = Dataset


class DataOutputResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_output = db.scalars(
                select(DataOutput).where(DataOutput.id == obj)
            ).one_or_none()
            if data_output:
                return data_output.owner_id
        return cls.DEFAULT


class DataProductMembershipResolver(SubjectResolver):
    model: Model = DataProduct

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            membership = db.scalars(
                select(DataProductMembership).where(DataProductMembership.id == obj)
            ).one_or_none()
            if membership:
                return membership.data_product_id
        return cls.DEFAULT


class DataOutputDatasetAssociationResolver(SubjectResolver):
    model: Model = Dataset

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_output_dataset = db.scalars(
                select(DataOutputDatasetAssociation).where(
                    DataOutputDatasetAssociation.id == obj
                )
            ).one_or_none()
            if data_output_dataset:
                return data_output_dataset.dataset_id
        return cls.DEFAULT


class DataProductDatasetAssociationResolver(SubjectResolver):
    model: Model = Dataset

    @classmethod
    def resolve(cls, request: Request, key: str, db: Session = Depends(get_db_session)):
        obj = DataProductResolver.resolve(request, key, db)
        if obj != cls.DEFAULT:
            data_product_dataset = db.scalars(
                select(DataProductDatasetAssociation).where(
                    DataProductDatasetAssociation.id == obj
                )
            ).one_or_none()
            if data_product_dataset:
                return data_product_dataset.dataset_id
        return cls.DEFAULT


class Authorization(metaclass=Singleton):

    def __init__(self, enforcer: AsyncEnforcer = None) -> None:
        self._enforcer: AsyncEnforcer = cast(AsyncEnforcer, enforcer)
        self._cache: Cache = LRUCache(maxsize=settings.AUTHORIZER_CACHE_SIZE)

    @classmethod
    async def initialize(cls) -> "Authorization":
        model_location = Path(__file__).parent / "rbac_model.conf"
        enforcer = await cls._construct_enforcer(str(model_location))
        return cls(enforcer)

    @staticmethod
    async def _construct_enforcer(model: str) -> AsyncEnforcer:
        """Initializes the casbin table in the DB and constructs the enforcer."""
        url = database.get_url(async_=True)
        adapter = sqlalchemy_adapter.Adapter(url, warning=False)
        await adapter.create_table()
        return AsyncEnforcer(model, adapter)

    @classmethod
    def enforce(
        cls,
        action: AuthorizationAction,
        resolver: type[SubjectResolver],
        *,
        object_id: str = "id",
    ) -> Callable[[Request, User, Session], None]:
        def inner(
            request: Request,
            user: User = Depends(get_authenticated_user),
            db: Session = Depends(get_db_session),
        ) -> None:
            if not settings.AUTHORIZER_ENABLED:
                return
            obj = resolver.resolve(request, object_id, db)
            dom = resolver.resolve_domain(db, obj)

            if not cls().has_access(sub=str(user.id), dom=dom, obj=obj, act=action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to perform this action",
                )

        return inner

    @cachedmethod(lambda self: self._cache)
    def has_access(
        self, *, sub: str, dom: str, obj: str, act: AuthorizationAction
    ) -> bool:
        if not settings.AUTHORIZER_ENABLED:
            return False

        enforcer: AsyncEnforcer = self._enforcer
        return enforcer.enforce(sub, dom, obj, str(act))

    def _after_update(self) -> None:
        """The cache should be purged when the casbin database is altered,
        otherwise we risk returning stale results.
        """
        self._cache.clear()

    async def sync_role_permissions(
        self, *, role_id: str, actions: Sequence[AuthorizationAction]
    ) -> None:
        """Creates or updates the permissions for the chosen role."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_policy(0, role_id)

        policies = [(role_id, str(action)) for action in actions]
        await enforcer.add_policies(policies)

        self._after_update()

    async def sync_everyone_role_permissions(
        self, *, actions: Sequence[AuthorizationAction]
    ) -> None:
        """Updates the permissions belonging to the 'everyone' role."""
        await self.sync_role_permissions(role_id="*", actions=actions)

    async def remove_role_permissions(self, *, role_id: str) -> None:
        """Removes all the permissions for the chosen role."""
        await self.sync_role_permissions(role_id=role_id, actions=())

    async def assign_resource_role(
        self, *, user_id: str, role_id: str, resource_id: str
    ) -> None:
        """Creates an entry in the casbin table,
        assigning the user a role for the chosen resource."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.add_named_grouping_policy("g", user_id, role_id, resource_id)
        self._after_update()

    async def revoke_resource_role(
        self, *, user_id: str, role_id: str, resource_id: str
    ) -> None:
        """Deletes the entry in the casbin table,
        revoking the role for the chosen resource and user."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_named_grouping_policy("g", user_id, role_id, resource_id)
        self._after_update()

    async def assign_domain_role(
        self, *, user_id: str, role_id: str, domain_id: str
    ) -> None:
        """Creates an entry in the casbin table,
        assigning the user a role for the chosen domain."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.add_named_grouping_policy("g2", user_id, role_id, domain_id)
        self._after_update()

    async def revoke_domain_role(
        self, *, user_id: str, role_id: str, domain_id: str
    ) -> None:
        """Deletes the entry in the casbin table,
        revoking the role for the chosen domain and user."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_named_grouping_policy("g2", user_id, role_id, domain_id)
        self._after_update()

    async def assign_global_role(self, *, user_id: str, role_id: str) -> None:
        """Creates an entry in the casbin table,
        assigning the user the chosen global role."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.add_named_grouping_policy("g3", user_id, role_id)
        self._after_update()

    async def revoke_global_role(self, *, user_id: str, role_id: str) -> None:
        """Deletes the entry in the casbin table,
        revoking the chosen global role for the user."""
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_named_grouping_policy("g3", user_id, role_id)
        self._after_update()

    async def assign_admin_role(self, *, user_id: str) -> None:
        """Creates an entry in the casbin table, assigning the user the admin role."""
        await self.assign_global_role(user_id=user_id, role_id="*")

    async def revoke_admin_role(self, *, user_id: str) -> None:
        """Deletes the entry in the casbin table, assigning the user the admin role."""
        await self.revoke_global_role(user_id=user_id, role_id="*")

    async def clear_assignments_for_user(self, *, user_id: str) -> None:
        """Removes all role assignments for a user inside the casbin table.
        Should be called when a user is removed.
        """
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_named_grouping_policy("g", 0, user_id)
        await enforcer.remove_filtered_named_grouping_policy("g2", 0, user_id)
        await enforcer.remove_filtered_named_grouping_policy("g3", 0, user_id)
        self._after_update()

    async def clear_assignments_for_resource_role(self, *, role_id: str) -> None:
        """Removes all assignments of a resource role inside the casbin table.
        Should be called when a resource role is removed.
        """
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_named_grouping_policy("g", 1, role_id)
        self._after_update()

    async def clear_assignments_for_domain_role(self, *, role_id: str) -> None:
        """Removes all assignments of a domain role inside the casbin table.
        Should be called when a domain role is removed.
        """
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_named_grouping_policy("g2", 1, role_id)
        self._after_update()

    async def clear_assignments_for_global_role(self, *, role_id: str) -> None:
        """Removes all assignments of a global role inside the casbin table.
        Should be called when a global role is removed.
        """
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_named_grouping_policy("g3", 1, role_id)
        self._after_update()

    async def clear_assignments_for_resource(self, *, resource_id: str) -> None:
        """Removes all assignments to a resource inside the casbin table.
        Should be called when a resource is removed.
        """
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_named_grouping_policy("g", 2, resource_id)
        self._after_update()

    async def clear_assignments_for_domain(self, *, domain_id: str) -> None:
        """Removes all assignments to a domain inside the casbin table.
        Should be called when a domain is removed.
        """
        enforcer: AsyncEnforcer = self._enforcer
        await enforcer.remove_filtered_named_grouping_policy("g2", 2, domain_id)
        self._after_update()
