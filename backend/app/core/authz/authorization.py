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
        """Initializes the casbin table in the DB and constructs the enforcer."""
        url = database.get_url(async_=True)
        adapter = sqlalchemy_adapter.Adapter(url, warning=False)
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

    async def sync_role_permissions(
        self, *, role_id: str, actions: Sequence[AuthorizationAction]
    ) -> None:
        """Creates or updates the permissions for the chosen role."""
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_filtered_policy(0, role_id)

        policies = [(role_id, str(action)) for action in actions]
        await enforcer.add_policies(policies)

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
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.add_named_grouping_policy("g", user_id, role_id, resource_id)

    async def revoke_resource_role(
        self, *, user_id: str, role_id: str, resource_id: str
    ) -> None:
        """Deletes the entry in the casbin table,
        assigning the user the role for the chosen resource."""
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_named_grouping_policy("g", user_id, role_id, resource_id)

    async def assign_domain_role(
        self, *, user_id: str, role_id: str, domain_id: str
    ) -> None:
        """Creates an entry in the casbin table,
        assigning the user a role for the chosen domain."""
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.add_named_grouping_policy("g2", user_id, role_id, domain_id)

    async def revoke_domain_role(
        self, *, user_id: str, role_id: str, domain_id: str
    ) -> None:
        """Deletes the entry in the casbin table,
        assigning the user the role for the chosen domain."""
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_named_grouping_policy("g2", user_id, role_id, domain_id)

    async def assign_admin_role(self, *, user_id: str) -> None:
        """Creates an entry in the casbin table, assigning the user the admin role."""
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.add_named_grouping_policy("g3", user_id, "*")

    async def revoke_admin_role(self, *, user_id: str) -> None:
        """Deletes the entry in the casbin table, assigning the user the admin role."""
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_named_grouping_policy("g3", user_id, "*")

    async def clear_assignments_for_user(self, *, user_id: str) -> None:
        """Removes all role assignments for a user inside the casbin table.
        Should be called when a user is removed.
        """
        enforcer: AsyncEnforcer = self.enforcer

        await enforcer.remove_filtered_named_grouping_policy("g", 0, user_id)
        await enforcer.remove_filtered_named_grouping_policy("g2", 0, user_id)
        await enforcer.remove_filtered_named_grouping_policy("g3", 0, user_id)

    async def clear_assignments_for_resource_role(self, *, role_id: str) -> None:
        """Removes all assignments of a resource role inside the casbin table.
        Should be called when a resource role is removed.
        """
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_filtered_named_grouping_policy("g", 1, role_id)

    async def clear_assignments_for_domain_role(self, *, role_id: str) -> None:
        """Removes all assignments of a domain role inside the casbin table.
        Should be called when a domain role is removed.
        """
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_filtered_named_grouping_policy("g2", 1, role_id)

    async def clear_assignments_for_resource(self, *, resource_id: str) -> None:
        """Removes all assignments of a resource role inside the casbin table.
        Should be called when a resource role is removed.
        """
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_filtered_named_grouping_policy("g", 2, resource_id)

    async def clear_assignments_for_domain(self, *, domain_id: str) -> None:
        """Removes all assignments of a resource role inside the casbin table.
        Should be called when a domain role is removed.
        """
        enforcer: AsyncEnforcer = self.enforcer
        await enforcer.remove_filtered_named_grouping_policy("g2", 2, domain_id)
