from contextlib import contextmanager
from typing import Iterable, Iterator, Optional
from uuid import UUID

from sqlalchemy import ColumnElement, event, false, or_, select, true
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import InputPort
from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment,
)
from app.core.auth.db_utils import is_system_account, is_user_admin
from app.data_products.model import DataProduct, DataProductVisibility
from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.model import OutputPort
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import (
    SKIP_DATA_PRODUCT_VISIBILITY_FILTER,
    SKIP_OUTPUT_PORT_ACCESS_FUNCTION_FILTER,
    UNFILTERED,
)
from app.groups.model import GroupMembership

_CURRENT_USER = "current_user_id"
_OPEN_ACCESS_FUNCTIONS = (
    OutputPortAccessFunction.UNRESTRICTED,
    OutputPortAccessFunction.RESTRICTED,
)


@contextmanager
def acting_as(session: Session, user_id: Optional[UUID]) -> Iterator[Session]:
    """A session nobody acts as sees everything."""
    previous = session.info.get(_CURRENT_USER)
    session.info[_CURRENT_USER] = user_id
    try:
        yield session
    finally:
        session.info[_CURRENT_USER] = previous


def output_port_visible_ignoring_consumption(
    db: Session, output_port: type[OutputPort]
) -> ColumnElement[bool]:
    user_id = _current_user(db)
    if user_id is None:
        return true()
    return _output_port_visible_ignoring_consumption(output_port, user_id)


def member_of(db: Session, data_product_id) -> ColumnElement[bool]:
    user_id = _current_user(db)
    if user_id is None:
        return false()
    return _member(data_product_id, user_id)


def visible_ids(db: Session, ids: Iterable[UUID]) -> set[UUID]:
    """Unknown ids are left out."""
    ids = set(ids)
    user_id = _current_user(db)
    if user_id is None or not ids:
        return ids
    adp = AbstractDataProduct.__table__
    return set(
        db.scalars(
            select(adp.c.id).where(
                adp.c.id.in_(ids),
                or_(
                    adp.c.abstract_data_product_type
                    != AbstractDataProductType.DATA_PRODUCT,
                    _data_product_id_visible(adp.c.id, user_id),
                ),
            ),
            execution_options=UNFILTERED,
        )
    )


@event.listens_for(Session, "do_orm_execute")
def _filter_to_visible_rows(state: ORMExecuteState) -> None:
    if not state.is_select:
        return
    user_id = state.session.info.get(_CURRENT_USER)
    if user_id is None:
        return

    criteria = []
    if not state.execution_options.get(SKIP_DATA_PRODUCT_VISIBILITY_FILTER):
        criteria += [
            with_loader_criteria(
                DataProduct,
                lambda cls: _data_product_visible(cls, user_id),
                include_aliases=True,
            ),
            with_loader_criteria(
                AbstractDataProduct,
                lambda cls: _abstract_data_product_visible(cls, user_id),
                include_aliases=True,
            ),
            with_loader_criteria(
                TechnicalAsset,
                lambda cls: _technical_asset_visible(cls, user_id),
                include_aliases=True,
            ),
        ]
    if not state.execution_options.get(SKIP_OUTPUT_PORT_ACCESS_FUNCTION_FILTER):
        criteria.append(
            with_loader_criteria(
                OutputPort,
                lambda cls: _output_port_visible(cls, user_id),
                include_aliases=True,
            )
        )
    if criteria:
        state.statement = state.statement.options(*criteria)


def _current_user(db: Session) -> Optional[UUID]:
    return db.info.get(_CURRENT_USER)


def _data_product_visible(data_product, user_id: UUID) -> ColumnElement[bool]:
    return or_(
        data_product.visibility == DataProductVisibility.DISCOVERABLE,
        _member(data_product.id, user_id),
        _privileged(user_id),
    )


def _abstract_data_product_visible(
    abstract_data_product, user_id: UUID
) -> ColumnElement[bool]:
    return or_(
        abstract_data_product.abstract_data_product_type
        != AbstractDataProductType.DATA_PRODUCT,
        _data_product_id_visible(abstract_data_product.id, user_id),
    )


def _technical_asset_visible(technical_asset, user_id: UUID) -> ColumnElement[bool]:
    return _data_product_id_visible(technical_asset.owner_id, user_id)


def _output_port_visible(output_port, user_id: UUID) -> ColumnElement[bool]:
    return or_(
        _output_port_visible_ignoring_consumption(output_port, user_id),
        _consumes(output_port.id, user_id),
    )


def _output_port_visible_ignoring_consumption(
    output_port, user_id: UUID
) -> ColumnElement[bool]:
    return or_(
        output_port.access_function.in_(_OPEN_ACCESS_FUNCTIONS),
        _has_output_port_role(output_port.id, user_id),
        _member(output_port.data_product_id, user_id),
        _privileged(user_id),
    )


def _data_product_id_visible(data_product_id, user_id: UUID) -> ColumnElement[bool]:
    # Built on the Core table: nested in a subquery, the ORM DataProduct would be
    # adapted to the outer alias through joined table inheritance and the EXISTS
    # would turn into an always true cross join.
    data_products = DataProduct.__table__
    return (
        select(data_products.c.id)
        .where(
            data_products.c.id == data_product_id,
            or_(
                data_products.c.visibility == DataProductVisibility.DISCOVERABLE,
                _member(data_products.c.id, user_id),
                _privileged(user_id),
            ),
        )
        .correlate_except(data_products)
        .exists()
    )


def _member(data_product_id, user_id: UUID) -> ColumnElement[bool]:
    assignments = DataProductRoleAssignment.__table__
    memberships = GroupMembership.__table__
    group_ids = (
        select(memberships.c.group_id)
        .where(memberships.c.member_identity_id == user_id)
        .correlate_except(memberships)
    )
    return (
        select(assignments.c.id)
        .where(
            assignments.c.data_product_id == data_product_id,
            or_(
                assignments.c.identity_id == user_id,
                assignments.c.identity_id.in_(group_ids),
            ),
            assignments.c.decision == DecisionStatus.APPROVED,
        )
        .correlate_except(assignments)
        .exists()
    )


def _consumes(output_port_id, user_id: UUID) -> ColumnElement[bool]:
    input_ports = InputPort.__table__
    return (
        select(input_ports.c.id)
        .where(
            input_ports.c.dataset_id == output_port_id,
            input_ports.c.status == InputPortStatus.APPROVED,
            _member(input_ports.c.consuming_abstract_data_product_id, user_id),
        )
        .correlate_except(input_ports)
        .exists()
    )


def _has_output_port_role(output_port_id, user_id: UUID) -> ColumnElement[bool]:
    # ponytail: direct Output Port roles are user only, no groups; the Output Port role rework replaces this.
    assignments = DatasetRoleAssignment.__table__
    return (
        select(assignments.c.id)
        .where(
            assignments.c.dataset_id == output_port_id,
            assignments.c.user_id == user_id,
            assignments.c.decision == DecisionStatus.APPROVED,
        )
        .correlate_except(assignments)
        .exists()
    )


def _privileged(user_id: UUID) -> ColumnElement[bool]:
    return or_(is_user_admin(user_id), is_system_account(user_id))
