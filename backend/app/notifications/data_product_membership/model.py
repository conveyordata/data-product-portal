from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.data_product_memberships.model import DataProductMembership
from app.notifications.model import Notification


class DataProductMembershipNotification(Notification):
    data_product_membership_id: Mapped[UUID] = Column(
        ForeignKey("data_product_memberships.id")
    )
    data_product_membership: Mapped["DataProductMembership"] = relationship()
    __mapper_args__ = {
        "polymorphic_identity": "DataProductMembershipNotification",
    }
