from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from app.data_products.output_ports.announcements.enums import AnnouncementType
from app.shared.schema import ORMModel
from app.users.schema import User


class Announcement(ORMModel):
    id: UUID
    output_port_id: UUID
    type: AnnouncementType
    title: str
    message: str
    author: Optional[User]
    created_at: datetime


class GetAnnouncementsResponse(ORMModel):
    announcements: Sequence[Announcement]


class CreateAnnouncementResponse(ORMModel):
    id: UUID
