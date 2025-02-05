from collections.abc import Callable
from pathlib import Path
from typing import cast

import casbin_async_sqlalchemy_adapter as sqlalchemy_adapter
from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException, status

from app.core.auth.auth import get_authenticated_user
from app.database import database
from app.users.schema import User

from .actions import AuthorizationAction
from .parameters import AuthorizationDep


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


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
        cls, action: AuthorizationAction
    ) -> Callable[[AuthorizationDep, User], None]:
        def inner(
            params: AuthorizationDep,
            user: User = Depends(get_authenticated_user),
        ) -> None:
            return cls()._enforce(
                sub=str(user.id),
                dom=params.domain,
                obj=params.object_id,
                act=action,
            )

        return inner

    def _enforce(self, *, sub: str, dom: str, obj: str, act: str) -> None:
        enforcer: AsyncEnforcer = self.enforcer
        if not enforcer.enforce(sub, dom, obj, act):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action",
            )
