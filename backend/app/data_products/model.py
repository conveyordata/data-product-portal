import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, event, func, or_, select
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    Session,
    column_property,
    mapped_column,
    relationship,
    with_loader_criteria,
)
from sqlalchemy.sql.visitors import iterate

from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.model import DataProductType
from app.configuration.tags.model import Tag, tag_data_product_table
from app.core.auth.auth import SYSTEM_ACCOUNT_BOT_EXTERNAL_ID
from app.core.webhooks.events import (
    DataProductEvent,
)
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import ensure_exists
from app.database.event_mixin import EventTrackedMixin

if TYPE_CHECKING:
    from app.configuration.data_product_lifecycles.model import DataProductLifecycle
    from app.configuration.data_product_settings.model import DataProductSettingValue
    from app.data_products.output_ports.model import (
        OutputPort,
    )


class DataProductVisibility(enum.Enum):
    HIDDEN = "hidden"
    DISCOVERABLE = "discoverable"


def _has_user_access_to_hidden_data_product(cls, user_id: uuid.UUID):
    return (
        select(DataProductRoleAssignment.id)
        .where(DataProductRoleAssignment.data_product_id == cls.id)
        .where(DataProductRoleAssignment.user_id == user_id)
        .where(DataProductRoleAssignment.decision == DecisionStatus.APPROVED)
        .exists()
    )


def _is_user_admin(user_id: uuid.UUID):
    from app.users.model import User

    return (
        select(User.id)
        .where(User.id == user_id)
        .where(User.admin_expiry > func.now())
        .exists()
    )


def _is_system_account(user_id: uuid.UUID):
    from app.users.model import User

    return (
        select(User.id)
        .where(User.id == user_id)
        .where(User.external_id == SYSTEM_ACCOUNT_BOT_EXTERNAL_ID)
        .exists()
    )


def _visibility_filter_for_user(user_id: uuid.UUID):
    return or_(
        DataProduct.visibility != DataProductVisibility.HIDDEN,
        _has_user_access_to_hidden_data_product(DataProduct, user_id),
        _is_user_admin(user_id),
        _is_system_account(user_id),
    )


def _statement_references_data_product(statement):
    try:
        selected_columns = list(statement.selected_columns)
    except Exception:
        selected_columns = []

    if not selected_columns:
        return False

    for selected in selected_columns:
        for node in iterate(selected, {}):
            if getattr(node, "table", None) is DataProduct.__table__:
                return True

    return False


class DataProduct(
    AbstractDataProduct,
    EventTrackedMixin,
):
    __tablename__ = "data_products"

    id: Mapped[UUID] = mapped_column(
        "id", ForeignKey("abstract_data_products.id"), primary_key=True
    )
    about = Column(String)
    usage = Column(String, nullable=True)
    visibility = mapped_column(
        SAEnum(
            DataProductVisibility,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=DataProductVisibility.DISCOVERABLE,
    )

    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )

    type: Mapped[DataProductType] = relationship(
        back_populates="data_products", lazy="joined"
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="data_products", lazy="joined"
    )
    assignments: Mapped[list["DataProductRoleAssignment"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductRoleAssignment.decision, DataProductRoleAssignment.requested_on",
        lazy="raise",
    )
    datasets: Mapped[list["OutputPort"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_data_product_table, back_populates="data_products", lazy="raise"
    )
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
        lazy="raise",
    )
    data_outputs: Mapped[list["TechnicalAsset"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    user_count = column_property(
        select(func.count(DataProductRoleAssignment.id))
        .where(DataProductRoleAssignment.data_product_id == id)
        .where(DataProductRoleAssignment.decision == DecisionStatus.APPROVED)
        .correlate_except(DataProductRoleAssignment)
        .scalar_subquery()
    )

    data_outputs_count = column_property(
        select(func.count(TechnicalAsset.id))
        .where(TechnicalAsset.owner_id == id)
        .correlate_except(TechnicalAsset)
        .scalar_subquery()
    )

    __mapper_args__ = {
        "polymorphic_identity": AbstractDataProductType.DATA_PRODUCT,
    }

    def to_event(self) -> DataProductEvent:
        return DataProductEvent(
            id=self.id,
        )


def ensure_data_product_exists(
    data_product_id: UUID, db: Session, **kwargs
) -> DataProduct:
    return ensure_exists(data_product_id, db, DataProduct, **kwargs)


@event.listens_for(Session, "do_orm_execute")
def enforce_hidden_data_product_filter(execute_state):
    if not execute_state.is_select:
        return

    # Refreshing an expired scalar attribute is not a new application-level
    # query; the row was already authorized when originally loaded, so don't
    # re-apply/require the visibility filter here. Relationship loads (lazy
    # loading a collection/association) can return rows that were never
    # authorized before, so those must still go through the filter.
    if execute_state.is_column_load:
        return

    if execute_state.execution_options.get("skip_data_product_visibility_filter"):
        return

    user_id = execute_state.session.info.get("current_user_id")

    # ORM entity loads use loader criteria. Scalar queries that directly select
    # DataProduct columns (for example select(DataProduct.id)) do not carry an
    # ORM entity description, but they still need the same visibility guard.
    is_data_product_query = any(
        desc.get("entity") is DataProduct
        for desc in execute_state.statement.column_descriptions
    ) or _statement_references_data_product(execute_state.statement)

    if not is_data_product_query:
        return

    if user_id is None:
        raise Exception(
            "User id must be set when skip_data_product_visibility_filter is False or not set"
        )

    if any(
        desc.get("entity") is DataProduct
        for desc in execute_state.statement.column_descriptions
    ):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                DataProduct,
                lambda cls: _visibility_filter_for_user(user_id),
                include_aliases=True,
            )
        )
        return

    execute_state.statement = execute_state.statement.where(
        _visibility_filter_for_user(user_id)
    )
