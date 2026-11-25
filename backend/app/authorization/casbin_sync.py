from collections.abc import Iterable, Iterator
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import TypedReturnsRows

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.admin import (
    admin_identity_ids,
    is_admin_role,
)
from app.authorization.role_assignments.global_.model import GlobalRoleAssignment
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment,
)
from app.authorization.roles.model import Role
from app.authorization.roles.schema import Prototype
from app.core.authz import CasbinPolicies
from app.core.authz.rules import (
    EVERYONE,
    READER_PERMISSIONS,
    GlobalRole,
    Permission,
    ResourceRole,
    Rule,
    admin_rule,
    everyone_reads_data_product,
    everyone_reads_output_port,
    membership_rules,
)
from app.core.logging import logger
from app.data_products.model import DataProduct
from app.data_products.output_ports.model import OutputPort
from app.database.database import UNFILTERED
from app.database.visibility import (
    data_product_visible_to_everyone,
    output_port_visible_to_everyone,
)
from app.groups.model import GroupMembership


class CasbinSync:
    def __init__(self, db: Session) -> None:
        self.db = db

    def rebuild(self) -> None:
        rules = self.rules()
        added, removed = CasbinPolicies().replace_all(rules)
        logger.info(
            f"Authorization rebuild done - the casbin table now contains {len(rules)} rows"
            f" ({added} added, {removed} removed)"
        )

    def rules(self) -> set[Rule]:
        return {
            *self._permissions(),
            *self._resource_roles(),
            *self._readers(),
            *self._global_roles(),
            *self._group_members(),
        }

    def _permissions(self) -> Iterator[Permission]:
        for id, prototype, permissions in self._rows(
            select(Role.id, Role.prototype, Role.permissions)
        ):
            role = EVERYONE if prototype == Prototype.EVERYONE else id
            yield from (Permission(role, action) for action in permissions)

    def _resource_roles(self) -> Iterator[ResourceRole]:
        for identity_id, role_id, data_product_id in self._rows(
            select(
                DataProductRoleAssignment.identity_id,
                DataProductRoleAssignment.role_id,
                DataProductRoleAssignment.data_product_id,
            ).where(DataProductRoleAssignment.decision == DecisionStatus.APPROVED)
        ):
            yield ResourceRole(identity_id, role_id, data_product_id)
        for user_id, role_id, output_port_id in self._rows(
            select(
                DatasetRoleAssignment.user_id,
                DatasetRoleAssignment.role_id,
                DatasetRoleAssignment.output_port_id,
            ).where(DatasetRoleAssignment.decision == DecisionStatus.APPROVED)
        ):
            yield ResourceRole(user_id, role_id, output_port_id)

    def _readers(self) -> Iterator[Rule]:
        yield from READER_PERMISSIONS
        for (data_product_id,) in self._rows(
            select(DataProduct.id).where(data_product_visible_to_everyone(DataProduct))
        ):
            yield everyone_reads_data_product(data_product_id)
        for (output_port_id,) in self._rows(
            select(OutputPort.id).where(output_port_visible_to_everyone(OutputPort))
        ):
            yield everyone_reads_output_port(output_port_id)

    def _global_roles(self) -> Iterator[GlobalRole]:
        for identity_id, role_id in self._rows(
            select(
                GlobalRoleAssignment.identity_id, GlobalRoleAssignment.role_id
            ).where(
                GlobalRoleAssignment.decision == DecisionStatus.APPROVED,
                ~is_admin_role(GlobalRoleAssignment.role_id),
            )
        ):
            yield GlobalRole(identity_id, role_id)
        for (identity_id,) in self._rows(admin_identity_ids()):
            yield admin_rule(identity_id)

    def _group_members(self) -> Iterator[Rule]:
        for member_id, group_id in self._rows(
            select(GroupMembership.member_identity_id, GroupMembership.group_id)
        ):
            yield from membership_rules(member_id, group_id)

    def _rows[*Ts = *tuple[Any, ...]](
        self, statement: TypedReturnsRows[*Ts]
    ) -> Iterable[tuple[*Ts]]:
        return self.db.execute(statement, execution_options=UNFILTERED).tuples()
