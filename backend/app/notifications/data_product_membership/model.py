from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.notifications.base_model import BaseNotificationConfiguration


class DataProductMembershipNotification(BaseNotificationConfiguration):
    data_product_membership_id: Mapped[UUID] = Column(
        ForeignKey("data_product_memberships.id")
    )
    __mapper_args__ = {
        "polymorphic_identity": "DataProductMembership",
    }
