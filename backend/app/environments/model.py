import uuid

from sqlalchemy import Boolean, Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

from .enums import PlatformTypes


class Environment(Base, BaseORM):
    __tablename__ = "environments"

    name = Column(String, primary_key=True)
    is_default = Column(Boolean, default=False)
    # type of a workspace? e.g. Dev has AWS but dev also
    # has Snowflake # AWS, Snowflake, Azure, Databricks
    # Custom specs per type?

    # Mvp: name and Iam role with data product name as a template
    # e.g. role-arn: iam-{{DataProductName}}-dev-iam-role

    platforms: Mapped[list["Platform"]] = relationship("Platform", backref="env")


class Platform(Base, BaseORM):
    __tablename__ = "platforms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Enum(PlatformTypes))
    settings = Column(String)
    environment: Mapped[String] = mapped_column(ForeignKey("environments.name"))
