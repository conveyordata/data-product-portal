from __future__ import annotations

import casbin_async_sqlalchemy_adapter as sqlalchemy_adapter
from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException, status

from app.authz.actions import AuthorizedAction
from app.core.auth.auth import get_authenticated_user
from app.settings import settings
from app.users.schema import User


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Authorization(metaclass=Singleton):

    def __init__(self) -> None:
        self.enforcer = self._construct_enforcer("./authz/rbac_model.conf")

    @staticmethod
    def _construct_enforcer(model: str) -> AsyncEnforcer:
        adapter = sqlalchemy_adapter.Adapter(
            f"postgresql+psycopg_async://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/casbin"
        )
        return AsyncEnforcer(model, adapter)

    @classmethod
    def enforce(
        cls, action: AuthorizedAction, user: User = Depends(get_authenticated_user)
    ):
        if not cls()._enforce(sub=user.id, act=action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action",
            )

    def _enforce(self, *, sub: str, dom: str, obj: str, act: str) -> bool:
        return self.enforcer.enforce(sub, dom, obj, act)
