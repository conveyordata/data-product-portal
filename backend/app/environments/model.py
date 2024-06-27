from sqlalchemy import Column, String, Boolean

from app.database.database import Base
from app.shared.model import BaseORM


class Environment(Base, BaseORM):
    __tablename__ = "environments"
    name = Column(String, primary_key=True)
    context = Column(String)
    is_default = Column(Boolean, default=False)
    # type of a workspace? e.g. Dev has AWS but dev also
    # has Snowflake # AWS, Snowflake, Azure, Databricks
    # Custom specs per type?

    # Mvp: name and Iam role with data product name as a template
    # e.g. role-arn: iam-{{DataProductName}}-dev-iam-role
