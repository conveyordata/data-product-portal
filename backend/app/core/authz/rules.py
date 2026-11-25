from typing import NamedTuple
from uuid import UUID

from .actions import AuthorizationAction

ID = str | UUID
EVERYONE = "*"
_ANY = "*"
DATA_PRODUCT_READER_ROLE = "/role/data-product-reader"
OUTPUT_PORT_READER_ROLE = "/role/output-port-reader"


class Permission(NamedTuple):
    role: ID
    action: int

    @property
    def ptype(self) -> str:
        return "p"


class ResourceRole(NamedTuple):
    identity: ID
    role: ID
    resource: ID

    @property
    def ptype(self) -> str:
        return "g"


class GlobalRole(NamedTuple):
    identity: ID
    role: ID

    @property
    def ptype(self) -> str:
        return "g3"


Rule = Permission | ResourceRole | GlobalRole

READER_PERMISSIONS = (
    Permission(
        DATA_PRODUCT_READER_ROLE, AuthorizationAction.HIDDEN__DATA_PRODUCT__READ
    ),
    Permission(OUTPUT_PORT_READER_ROLE, AuthorizationAction.HIDDEN__OUTPUT_PORT__READ),
)


def everyone_reads_data_product(data_product_id: ID) -> ResourceRole:
    return ResourceRole(EVERYONE, DATA_PRODUCT_READER_ROLE, data_product_id)


def everyone_reads_output_port(output_port_id: ID) -> ResourceRole:
    return ResourceRole(EVERYONE, OUTPUT_PORT_READER_ROLE, output_port_id)


def admin_rule(identity_id: ID) -> GlobalRole:
    return GlobalRole(identity_id, _ANY)


def membership_rules(member_id: ID, group_id: ID) -> tuple[ResourceRole, GlobalRole]:
    return ResourceRole(member_id, group_id, _ANY), GlobalRole(member_id, group_id)
