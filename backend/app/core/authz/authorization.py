from collections.abc import Callable
from pathlib import Path
from typing import Sequence, TypeAlias, Union
from uuid import UUID

import casbin_sqlalchemy_adapter as sqlalchemy_adapter
from cachetools import Cache, LRUCache, cachedmethod
from casbin import Enforcer
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database import database
from app.database.database import get_db_session
from app.settings import settings
from app.users.schema import User
from app.utils.singleton import Singleton

from .actions import AuthorizationAction
from .resolvers import SubjectResolver

ID: TypeAlias = Union[str, UUID]


class Authorization(metaclass=Singleton):

    def __init__(self) -> None:
        self._enforcer: Enforcer = self._initialize()
        self._cache: Cache = LRUCache(maxsize=settings.AUTHORIZER_CACHE_SIZE)

    @classmethod
    def _initialize(cls) -> Enforcer:
        model_location = Path(__file__).parent / "rbac_model.conf"
        enforcer = cls._construct_enforcer(str(model_location))
        enforcer.load_policy()
        return enforcer

    @staticmethod
    def _construct_enforcer(model: str) -> Enforcer:
        """Initializes the casbin table in the DB and constructs the enforcer."""
        adapter = sqlalchemy_adapter.Adapter(database.get_url())
        return Enforcer(model, adapter)

    @classmethod
    def deregister(cls):
        """Releases the enforcer from the singleton. Useful during testing."""
        Singleton.deregister(cls)

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
        enforcer: Enforcer = self._enforcer
        return enforcer.enforce(sub, dom, obj, str(act))

    def _after_update(self) -> None:
        """The cache should be purged when the casbin database is altered,
        otherwise we risk returning stale results.
        """
        self._cache.clear()

    def sync_role_permissions(
        self, *, role_id: ID, actions: Sequence[AuthorizationAction]
    ) -> bool:
        """Creates or updates the permissions for the chosen role."""
        enforcer: Enforcer = self._enforcer
        enforcer.remove_filtered_policy(0, role_id)

        policies = [(str(role_id), str(action)) for action in actions]
        updated = enforcer.add_policies(policies)
        self._after_update()
        return updated

    def sync_everyone_role_permissions(
        self, *, actions: Sequence[AuthorizationAction]
    ) -> bool:
        """Updates the permissions belonging to the 'everyone' role."""
        return self.sync_role_permissions(role_id="*", actions=actions)

    def remove_role_permissions(self, *, role_id: ID) -> bool:
        """Removes all the permissions for the chosen role."""
        return self.sync_role_permissions(role_id=role_id, actions=())

    def assign_resource_role(
        self, *, user_id: ID, role_id: ID, resource_id: ID
    ) -> bool:
        """Creates an entry in the casbin table,
        assigning the user a role for the chosen resource."""
        enforcer: Enforcer = self._enforcer
        updated = enforcer.add_named_grouping_policy(
            "g", str(user_id), str(role_id), str(resource_id)
        )
        self._after_update()
        return updated

    def revoke_resource_role(
        self, *, user_id: ID, role_id: ID, resource_id: ID
    ) -> bool:
        """Deletes the entry in the casbin table,
        revoking the role for the chosen resource and user."""
        enforcer: Enforcer = self._enforcer
        updated = enforcer.remove_named_grouping_policy(
            "g", str(user_id), str(role_id), str(resource_id)
        )
        self._after_update()
        return updated

    def has_resource_role(self, *, user_id: ID, role_id: ID, resource_id: ID) -> bool:
        """Determines whether this resource role is assigned to the chosen user."""
        enforcer: Enforcer = self._enforcer
        return enforcer.has_named_grouping_policy(
            "g", str(user_id), str(role_id), str(resource_id)
        )

    def assign_domain_role(self, *, user_id: ID, role_id: ID, domain_id: ID) -> bool:
        """Creates an entry in the casbin table,
        assigning the user a role for the chosen domain."""
        enforcer: Enforcer = self._enforcer
        updated = enforcer.add_named_grouping_policy(
            "g2", str(user_id), str(role_id), str(domain_id)
        )
        self._after_update()
        return updated

    def revoke_domain_role(self, *, user_id: ID, role_id: ID, domain_id: ID) -> bool:
        """Deletes the entry in the casbin table,
        revoking the role for the chosen domain and user."""
        enforcer: Enforcer = self._enforcer
        updated = enforcer.remove_named_grouping_policy(
            "g2", str(user_id), str(role_id), str(domain_id)
        )
        self._after_update()
        return updated

    def has_domain_role(self, *, user_id: ID, role_id: ID, domain_id: ID) -> bool:
        """Determines whether this domain role is assigned to chosen user."""
        enforcer: Enforcer = self._enforcer
        return enforcer.has_named_grouping_policy(
            "g2", str(user_id), str(role_id), str(domain_id)
        )

    def assign_global_role(self, *, user_id: ID, role_id: ID) -> bool:
        """Creates an entry in the casbin table,
        assigning the user the chosen global role."""
        enforcer: Enforcer = self._enforcer
        updated = enforcer.add_named_grouping_policy("g3", str(user_id), str(role_id))
        self._after_update()
        return updated

    def revoke_global_role(self, *, user_id: ID, role_id: ID) -> bool:
        """Deletes the entry in the casbin table,
        revoking the chosen global role for the user."""
        enforcer: Enforcer = self._enforcer
        updated = enforcer.remove_named_grouping_policy(
            "g3", str(user_id), str(role_id)
        )
        self._after_update()
        return updated

    def has_global_role(self, *, user_id: ID, role_id: ID) -> bool:
        """Determines whether this global role is assigned to the chosen user."""
        enforcer: Enforcer = self._enforcer
        return enforcer.has_named_grouping_policy("g3", str(user_id), str(role_id))

    def assign_admin_role(self, *, user_id: ID) -> bool:
        """Creates an entry in the casbin table, assigning the user the admin role."""
        return self.assign_global_role(user_id=user_id, role_id="*")

    def revoke_admin_role(self, *, user_id: ID) -> bool:
        """Deletes the entry in the casbin table, assigning the user the admin role."""
        return self.revoke_global_role(user_id=user_id, role_id="*")

    def has_admin_role(self, *, user_id: ID) -> bool:
        """Determines whether the admin role is assigned to the chosen user."""
        return self.has_global_role(user_id=user_id, role_id="*")

    def clear_assignments_for_user(self, *, user_id: ID) -> bool:
        """Removes all role assignments for a user inside the casbin table.
        Should be called when a user is removed.
        """
        value = str(user_id)

        enforcer: Enforcer = self._enforcer
        resource_updates = enforcer.remove_filtered_named_grouping_policy("g", 0, value)
        domain_updates = enforcer.remove_filtered_named_grouping_policy("g2", 0, value)
        global_updates = enforcer.remove_filtered_named_grouping_policy("g3", 0, value)
        self._after_update()
        return bool(resource_updates or domain_updates or global_updates)

    def clear_assignments_for_resource_role(self, *, role_id: ID) -> bool:
        """Removes all assignments of a resource role inside the casbin table.
        Should be called when a resource role is removed.
        """
        enforcer: Enforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy("g", 1, str(role_id))
        self._after_update()
        return bool(updates)

    def clear_assignments_for_domain_role(self, *, role_id: ID) -> bool:
        """Removes all assignments of a domain role inside the casbin table.
        Should be called when a domain role is removed.
        """
        enforcer: Enforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy("g2", 1, str(role_id))
        self._after_update()
        return bool(updates)

    def clear_assignments_for_global_role(self, *, role_id: ID) -> bool:
        """Removes all assignments of a global role inside the casbin table.
        Should be called when a global role is removed.
        """
        enforcer: Enforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy("g3", 1, str(role_id))
        self._after_update()
        return bool(updates)

    def clear_assignments_for_resource(self, *, resource_id: ID) -> bool:
        """Removes all assignments to a resource inside the casbin table.
        Should be called when a resource is removed.
        """
        enforcer: Enforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy(
            "g", 2, str(resource_id)
        )
        self._after_update()
        return bool(updates)

    def clear_assignments_for_domain(self, *, domain_id: ID) -> bool:
        """Removes all assignments to a domain inside the casbin table.
        Should be called when a domain is removed.
        """
        enforcer: Enforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy(
            "g2", 2, str(domain_id)
        )
        self._after_update()
        return bool(updates)
