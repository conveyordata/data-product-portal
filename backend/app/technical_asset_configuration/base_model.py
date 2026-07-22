import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.database.database import Base
from app.shared.model import BaseORM


class TechnicalAssetConfiguration(Base, BaseORM):
    """
    Base table for all data output configurations.
    Contains the ID, timestamps, and configuration_type discriminator.
    Each specific configuration type (Snowflake, Databricks, etc.) has its own table
    with additional columns, and references this table via foreign key on the id column.

    This uses Class Table Inheritance pattern to maintain referential integrity
    while allowing each configuration type to have its own dedicated table.

    The configuration_type field is used for:
    1. Pydantic serialization (discriminator for Union types)
    2. SQLAlchemy polymorphic loading (to load the correct subclass)

    In case of future performance issues these fields can be used in DataOutput directly, which would mean one less join.
    """

    __tablename__ = "data_output_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_type: Mapped[String] = Column(String)

    __mapper_args__ = {
        "polymorphic_on": "configuration_type",
        "polymorphic_identity": "data_output",
    }


class BaseTechnicalAssetConfiguration(TechnicalAssetConfiguration):
    """
    Abstract base class for specific configuration type tables.
    Each configuration type (Snowflake, Databricks, etc.) inherits from this
    and defines its own table with configuration-specific columns.

    The 'id' column in each child table is both a primary key AND a foreign key
    back to data_output_configurations.id, creating a Class Table Inheritance pattern.
    """

    __abstract__ = True  # This is an abstract base class, not a table

    id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
        primary_key=True,
    )
