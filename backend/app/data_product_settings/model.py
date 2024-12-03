import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.database import Base
from app.shared.model import BaseORM


class DataProductSetting(Base, BaseORM):
    __tablename__ = "data_product_settings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    tooltip = Column(String)
    type = Column(String)
    divider = Column(String)
