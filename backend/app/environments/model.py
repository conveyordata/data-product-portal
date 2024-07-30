from sqlalchemy import Boolean, Column, String

from app.database.database import Base
from app.shared.model import BaseORM


class Environment(Base, BaseORM):
    __tablename__ = "environments"

    name = Column(String, primary_key=True)
    is_default = Column(Boolean, default=False)
