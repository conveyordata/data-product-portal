import asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Sequence, cast

import casbin_async_sqlalchemy_adapter as sqlalchemy_adapter
from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException, Request, status

from app.core.auth.auth import get_authenticated_user
from app.database import database
from app.users.schema import User
from app.utils.singleton import Singleton

from .actions import AuthorizationAction


class Authorization(metaclass=Singleton):

    def __init__(self, enforcer: AsyncEnforcer = None) -> None:
        self.enforcer: AsyncEnforcer = cast(AsyncEnforcer, enforcer)

    @classmethod
    async def initialize(cls) -> "Authorization":
        model_location = Path(__file__).parent / "rbac_model.conf"
        enforcer = await cls._construct_enforcer(str(model_location))
        return cls(enforcer)

    @staticmethod
    async def _construct_enforcer(model: str) -> AsyncEnforcer:
        adapter = sqlalchemy_adapter.Adapter(database.get_url(async_=True))
        await adapter.create_table()
        return AsyncEnforcer(model, adapter)

    @classmethod
    def enforce(
        cls,
        action: AuthorizationAction,
        object_id: str = "object_id",
        domain: str = "domain",
    ) -> Callable[[Request, User], None]:
        def inner(
            request: Request,
            user: User = Depends(get_authenticated_user),
        ) -> None:
            obj = cls.resolve_parameter(request, object_id)
            dom = cls.resolve_parameter(request, domain)

            return cls()._enforce(
                sub=str(user.id),
                dom=dom,
                obj=obj,
                act=action,
            )

        return inner

    @staticmethod
    def resolve_parameter(request: Request, key: str, default: str = "*") -> str:
        if (result := request.query_params.get(key)) is not None:
            return cast(str, result)
        if (result := request.path_params.get(key)) is not None:
            return cast(str, result)

        return default

    def _enforce(self, *, sub: str, dom: str, obj: str, act: int) -> None:
        enforcer: AsyncEnforcer = self.enforcer
        if not enforcer.enforce(sub, dom, obj, str(act)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action",
            )

    async def sync_role(self, *, role_id: str, actions: Sequence[AuthorizationAction]):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.delete_permissions_for_user(role_id)

        add_permissions = (
            enforcer.add_permission_for_user(role_id, str(action)) for action in actions
        )
        await asyncio.gather(*add_permissions)

    async def sync_everyone_role(self, *, actions: Sequence[AuthorizationAction]):
        await self.sync_role(role_id="*", actions=actions)

    async def remove_role(self, role_id: str):
        await self.sync_role(role_id=role_id, actions=())

    async def assign_resource_role(
        self, *, user_id: str, role_id: str, resource_id: str
    ):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.add_named_grouping_policy("g", user_id, role_id, resource_id)

    async def revoke_resource_role(
        self, *, user_id: str, role_id: str, resource_id: str
    ):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_named_grouping_policy("g", user_id, role_id, resource_id)

    async def assign_domain_role(self, *, user_id: str, role_id: str, domain_id: str):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.add_named_grouping_policy("g2", user_id, role_id, domain_id)

    async def revoke_domain_role(self, *, user_id: str, role_id: str, domain_id: str):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_named_grouping_policy("g2", user_id, role_id, domain_id)

    async def assign_admin_role(self, *, user_id: str):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.add_named_grouping_policy("g3", user_id, "*")

    async def revoke_admin_role(self, *, user_id: str):
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_named_grouping_policy("g3", user_id, "*")
