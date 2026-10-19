from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Sequence,
    TypeAlias,
    Union,
    assert_never,
)
from uuid import UUID

import casbin_sqlalchemy_adapter as sqlalchemy_adapter
from cachetools import Cache, TTLCache, cachedmethod
from casbin import SyncedEnforcer, util
from fastapi import Depends, HTTPException, Request, status
from opentelemetry import trace
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.data_products.model import DataProductVisibility
from app.database import database
from app.database.deps import get_db_session
from app.settings import settings
from app.users.schema import User
from app.utils.singleton import Singleton

from .actions import AuthorizationAction
from .resolvers import SubjectResolver

if TYPE_CHECKING:
    from app.data_products.model import DataProduct

ID: TypeAlias = Union[str, UUID]

tracer = trace.get_tracer(__name__)


@dataclass(frozen=True)
class InputPortLink:
    consumer_id: str
    producer_data_product_id: str
    producer_output_port_id: str


def _has_access_through_consumer_role(
    enforcer: SyncedEnforcer,
    sub: str,
    role: str,
    resource: str,
    parent: str,
    action: str,
) -> bool:
    if action != str(AuthorizationAction.HIDDEN__OUTPUT_PORT__READ):
        return False
    linked_resources = enforcer.get_filtered_named_grouping_policy(
        "g4", 1, parent, resource
    )

    # g4 identifies consumers of the exact output port;
    # g checks whether the subject has the evaluated role on one of them.
    return any(
        enforcer.get_role_manager().has_link(sub, role, consumer_id)
        for consumer_id, _, _ in linked_resources
    )


class Authorization(metaclass=Singleton):
    def __init__(self) -> None:
        self._reloading = False
        self._adapter = sqlalchemy_adapter.Adapter(database.get_url())
        self._enforcer: SyncedEnforcer = self._initialize(self._adapter)
        self._cache: Cache = TTLCache(
            maxsize=settings.AUTHORIZER_CACHE_SIZE,
            ttl=settings.AUTHORIZER_AUTOLOAD_INTERVAL,
        )

    @classmethod
    def _initialize(cls, adapter: sqlalchemy_adapter.Adapter) -> SyncedEnforcer:
        model_location = Path(__file__).parent / "rbac_model.conf"
        enforcer = cls._construct_enforcer(str(model_location), adapter)
        enforcer.load_policy()
        return enforcer

    @staticmethod
    def _construct_enforcer(
        model: str, adapter: sqlalchemy_adapter.Adapter
    ) -> SyncedEnforcer:
        """Initializes the casbin table in the DB and constructs the enforcer."""
        enforcer = SyncedEnforcer(model, adapter)
        # Used to allow g(user, group, *) rules so users inherit group permissions
        enforcer.add_named_domain_matching_func("g", util.key_match)
        enforcer.add_function(
            "hasAccessThroughConsumerRole",
            partial(_has_access_through_consumer_role, enforcer),
        )
        if settings.AUTHORIZER_AUTOLOAD_ENABLED:
            enforcer.start_auto_load_policy(settings.AUTHORIZER_AUTOLOAD_INTERVAL)
        return enforcer

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
    ) -> Callable[[Request, User, Session], Awaitable[None]]:
        async def inner(
            request: Request,
            user: User = Depends(get_authenticated_user),
            db: Session = Depends(get_db_session, scope="function"),
        ) -> None:
            context = await resolver.resolve_context(request, object_id, db)

            if not cls().has_access(
                sub=str(user.id),
                dom=context.domain_id,
                obj=context.object_id,
                parent=context.parent_id,
                act=action,
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to perform this action",
                )

        return inner

    @cachedmethod(lambda self: self._cache)
    def has_access(
        self,
        *,
        sub: str,
        dom: str,
        obj: str,
        act: AuthorizationAction,
        parent: str = "*",
    ) -> bool:
        with tracer.start_as_current_span("has_access"):
            enforcer: SyncedEnforcer = self._enforcer
            return enforcer.enforce(sub, dom, obj, parent, str(act))

    def _after_update(self) -> None:
        """The cache should be purged when the casbin database is altered,
        otherwise we risk returning stale results.
        """
        self._cache.clear()

    def sync_role_permissions(
        self, *, role_id: ID, actions: Sequence[AuthorizationAction]
    ) -> bool:
        """Creates or updates the permissions for the chosen role."""
        enforcer: SyncedEnforcer = self._enforcer
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
        enforcer: SyncedEnforcer = self._enforcer
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
        enforcer: SyncedEnforcer = self._enforcer
        updated = enforcer.remove_named_grouping_policy(
            "g", str(user_id), str(role_id), str(resource_id)
        )
        self._after_update()
        return updated

    def sync_resource_roles(
        self, *, user_id: ID, role_id: ID, resource_ids: Sequence[ID], granted: bool
    ) -> None:
        enforcer: SyncedEnforcer = self._enforcer
        uid, rid = str(user_id), str(role_id)

        rules = [
            [uid, rid, str(r)]
            for r in resource_ids
            if enforcer.has_named_grouping_policy("g", uid, rid, str(r)) != granted
        ]
        if not rules:
            return

        if granted:
            enforcer.add_named_grouping_policies("g", rules)
        else:
            enforcer.remove_named_grouping_policies("g", rules)
        self._after_update()

    def has_resource_role(self, *, user_id: ID, role_id: ID, resource_id: ID) -> bool:
        """Determines whether this resource role is assigned to the chosen user."""
        enforcer: SyncedEnforcer = self._enforcer
        return enforcer.has_named_grouping_policy(
            "g", str(user_id), str(role_id), str(resource_id)
        )

    def add_input_port_link(
        self,
        *,
        consumer_id: ID,
        producer_data_product_id: ID,
        producer_output_port_id: ID,
    ):
        """
        Establishes an input port relationship between a consumer and a producer output
        port identified by the provided IDs. This ensures that a consumer can access
        a hidden data product, or private output port that it consumes.

        :param consumer_id: Identifier for the consumer entity.
        :param producer_data_product_id: Identifier for the producer's data product.
        :param producer_output_port_id: Identifier for the specific output port of the
            producer.
        """
        enforcer: SyncedEnforcer = self._enforcer
        enforcer.add_named_grouping_policy(
            "g4",
            str(consumer_id),
            str(producer_data_product_id),
            str(producer_output_port_id),
        )
        self._after_update()

    def remove_input_port_link(
        self,
        *,
        consumer_id: ID,
        producer_data_product_id: ID,
        producer_output_port_id: ID,
    ):
        enforcer: SyncedEnforcer = self._enforcer
        enforcer.remove_named_grouping_policy(
            "g4",
            str(consumer_id),
            str(producer_data_product_id),
            str(producer_output_port_id),
        )
        self._after_update()

    def get_input_port_link(
        self, *, producer_data_product_id: ID
    ) -> set[InputPortLink]:
        """Retrieves consumer links created with ``add_consumer_link``."""
        return {
            InputPortLink(
                consumer_id=consumer_id,
                producer_data_product_id=producer_data_product_id,
                producer_output_port_id=producer_output_port_id,
            )
            for consumer_id, producer_data_product_id, producer_output_port_id in self._enforcer.get_filtered_named_grouping_policy(
                "g4", 1, str(producer_data_product_id)
            )
        }

    def assign_domain_role(self, *, user_id: ID, role_id: ID, domain_id: ID) -> bool:
        """Creates an entry in the casbin table,
        assigning the user a role for the chosen domain."""
        enforcer: SyncedEnforcer = self._enforcer
        updated = enforcer.add_named_grouping_policy(
            "g2", str(user_id), str(role_id), str(domain_id)
        )
        self._after_update()
        return updated

    def pause_enforcer_for_reload(self) -> None:
        """This stops autoloading and auto policy saving of the enforcer.
        IT ALSO CLEARS ALL POLICIES FROM CASBIN.
        To be used when you want to recreate the casbin table.
        By pausing these it goes faster and avoids race conditions."""
        self._reloading = True
        self._enforcer.stop_auto_load_policy()
        self._enforcer.enable_auto_save(False)
        self._enforcer.clear_policy()

    def start_enforcer_after_reload(self) -> None:
        """This resumes autoloading and auto policy saving of the enforcer. It also flushes the current policy to the database.
        To be used when you want to recreate the casbin table, to be used after pause_enforcer_for_reload."""
        self._cache.clear()
        self._enforcer.build_role_links()  # Reconstructs the user → group → role graph to avoid stale user → group relationships
        self._enforcer.save_policy()
        if settings.AUTHORIZER_AUTOLOAD_ENABLED:
            self._enforcer.start_auto_load_policy(settings.AUTHORIZER_AUTOLOAD_INTERVAL)
        self._enforcer.enable_auto_save(True)
        self._reloading = False

    def revoke_domain_role(self, *, user_id: ID, role_id: ID, domain_id: ID) -> bool:
        """Deletes the entry in the casbin table,
        revoking the role for the chosen domain and user."""
        enforcer: SyncedEnforcer = self._enforcer
        updated = enforcer.remove_named_grouping_policy(
            "g2", str(user_id), str(role_id), str(domain_id)
        )
        self._after_update()
        return updated

    def has_domain_role(self, *, user_id: ID, role_id: ID, domain_id: ID) -> bool:
        """Determines whether this domain role is assigned to chosen user."""
        enforcer: SyncedEnforcer = self._enforcer
        return enforcer.has_named_grouping_policy(
            "g2", str(user_id), str(role_id), str(domain_id)
        )

    def assign_global_role(self, *, user_id: ID, role_id: ID) -> bool:
        """Creates an entry in the casbin table,
        assigning the user the chosen global role."""
        enforcer: SyncedEnforcer = self._enforcer
        updated = enforcer.add_named_grouping_policy("g3", str(user_id), str(role_id))
        self._after_update()
        return updated

    def revoke_global_role(self, *, user_id: ID, role_id: ID) -> bool:
        """Deletes the entry in the casbin table,
        revoking the chosen global role for the user."""
        enforcer: SyncedEnforcer = self._enforcer
        updated = enforcer.remove_named_grouping_policy(
            "g3", str(user_id), str(role_id)
        )
        self._after_update()
        return updated

    def has_global_role(self, *, user_id: ID, role_id: ID) -> bool:
        """Determines whether this global role is assigned to the chosen user."""
        enforcer: SyncedEnforcer = self._enforcer
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

        enforcer: SyncedEnforcer = self._enforcer
        resource_updates = enforcer.remove_filtered_named_grouping_policy("g", 0, value)
        domain_updates = enforcer.remove_filtered_named_grouping_policy("g2", 0, value)
        global_updates = enforcer.remove_filtered_named_grouping_policy("g3", 0, value)
        self._after_update()
        return bool(resource_updates or domain_updates or global_updates)

    def clear_assignments_for_identities(self, *, identity_ids: Sequence[ID]) -> bool:
        """Removes all role assignments for multiple identities."""
        values = {str(identity_id) for identity_id in identity_ids}
        if not values:
            return False

        enforcer: SyncedEnforcer = self._enforcer

        for policy_type in ("g", "g2", "g3"):
            for value in values:
                self._adapter.remove_filtered_policy(
                    "g",
                    policy_type,
                    0,
                    value,
                )

        enforcer.load_policy()
        self._after_update()
        return True

    def clear_assignments_for_resource_role(self, *, role_id: ID) -> bool:
        """Removes all assignments of a resource role inside the casbin table.
        Should be called when a resource role is removed.
        """
        enforcer: SyncedEnforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy("g", 1, str(role_id))
        self._after_update()
        return bool(updates)

    def clear_assignments_for_domain_role(self, *, role_id: ID) -> bool:
        """Removes all assignments of a domain role inside the casbin table.
        Should be called when a domain role is removed.
        """
        enforcer: SyncedEnforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy("g2", 1, str(role_id))
        self._after_update()
        return bool(updates)

    def clear_assignments_for_global_role(self, *, role_id: ID) -> bool:
        """Removes all assignments of a global role inside the casbin table.
        Should be called when a global role is removed.
        """
        enforcer: SyncedEnforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy("g3", 1, str(role_id))
        self._after_update()
        return bool(updates)

    def clear_assignments_for_resource(self, *, resource_id: ID) -> bool:
        """Removes all assignments to a resource inside the casbin table.
        Should be called when a resource is removed.
        """
        enforcer: SyncedEnforcer = self._enforcer
        role_updates = enforcer.remove_filtered_named_grouping_policy(
            "g", 2, str(resource_id)
        )
        source_link_updates = enforcer.remove_filtered_named_grouping_policy(
            "g4", 0, str(resource_id)
        )
        target_link_updates = enforcer.remove_filtered_named_grouping_policy(
            "g4", 1, str(resource_id)
        )
        output_port_link_updates = enforcer.remove_filtered_named_grouping_policy(
            "g4", 2, str(resource_id)
        )
        self._after_update()
        return bool(
            role_updates
            or source_link_updates
            or target_link_updates
            or output_port_link_updates
        )

    def clear_assignments_for_domain(self, *, domain_id: ID) -> bool:
        """Removes all assignments to a domain inside the casbin table.
        Should be called when a domain is removed.
        """
        enforcer: SyncedEnforcer = self._enforcer
        updates = enforcer.remove_filtered_named_grouping_policy(
            "g2", 2, str(domain_id)
        )
        self._after_update()
        return bool(updates)

    def has_read_access_to_data_product(
        self, current_user: User, data_product: "DataProduct"
    ) -> bool:

        # The check for visibility is a performance optimization to avoid unnecessary
        # has_access checks for discoverable data products.
        match data_product.visibility:
            case DataProductVisibility.DISCOVERABLE:
                return True
            case DataProductVisibility.HIDDEN:
                return self.has_access(
                    sub=str(current_user.id),
                    obj=str(data_product.id),
                    dom=str(data_product.domain_id),
                    act=AuthorizationAction.HIDDEN__DATA_PRODUCT__READ,
                )
            case _:
                assert_never(data_product.visibility)

    def assign_group_memberships(self, *, memberships: Sequence[tuple[ID, ID]]) -> bool:
        """
        Assign multiple member-to-group inheritance relationships.

        Evaluates previously existing policies to avoid failures when adding duplicates,
        as that will prevent the remaining policies from the batch to be added.
        """
        if not memberships:
            return False

        enforcer: SyncedEnforcer = self._enforcer
        if not self._reloading:
            enforcer.load_policy()

        resource_candidates = {
            (str(member_id), str(group_id), "*") for member_id, group_id in memberships
        }
        global_candidates = {
            (str(member_id), str(group_id)) for member_id, group_id in memberships
        }

        resource_policies = [
            list(policy)
            for policy in resource_candidates
            if not enforcer.has_named_grouping_policy("g", *policy)
        ]
        global_policies = [
            list(policy)
            for policy in global_candidates
            if not enforcer.has_named_grouping_policy("g3", *policy)
        ]

        resource_updates = (
            enforcer.add_named_grouping_policies("g", resource_policies)
            if resource_policies
            else False
        )
        global_updates = (
            enforcer.add_named_grouping_policies("g3", global_policies)
            if global_policies
            else False
        )

        # load_policy() may have changed local authorization state
        self._after_update()
        return bool(resource_updates or global_updates)

    def revoke_group_memberships(self, *, memberships: Sequence[tuple[ID, ID]]) -> bool:
        """Revoke multiple member-to-group inheritance relationships."""
        if not memberships:
            return False

        enforcer: SyncedEnforcer = self._enforcer

        resource_policies = {
            (str(member_id), str(group_id), "*") for member_id, group_id in memberships
        }
        global_policies = {
            (str(member_id), str(group_id)) for member_id, group_id in memberships
        }

        # Capture locally known policies before deleting persistence. These are
        # the policies whose local role links must also be removed.
        local_resource_policies = [
            list(policy)
            for policy in resource_policies
            if enforcer.has_named_grouping_policy("g", *policy)
        ]
        local_global_policies = [
            list(policy)
            for policy in global_policies
            if enforcer.has_named_grouping_policy("g3", *policy)
        ]

        # Delete persistence independently of this worker's local snapshot.
        for resource_policy in resource_policies:
            self._adapter.remove_policy("g", "g", list(resource_policy))
        for global_policy in global_policies:
            self._adapter.remove_policy("g", "g3", list(global_policy))

        # Update this worker's local policy model and role links. These calls may
        # issue redundant persistence deletes for locally known policies, which
        # are harmless.
        if local_resource_policies:
            enforcer.remove_named_grouping_policies(
                "g",
                local_resource_policies,
            )
        if local_global_policies:
            enforcer.remove_named_grouping_policies(
                "g3",
                local_global_policies,
            )

        self._after_update()
        return True
