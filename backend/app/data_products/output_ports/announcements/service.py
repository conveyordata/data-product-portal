from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.data_products.output_ports.announcements.model import (
    Announcement as AnnouncementModel,
)
from app.data_products.output_ports.announcements.schema_request import (
    CreateAnnouncement,
)
from app.database.database import ensure_exists
from app.users.model import User


class AnnouncementService:
    def __init__(self, db: Session):
        self.db = db

    def get_announcements(self, output_port_id: UUID) -> Sequence[AnnouncementModel]:
        return self.db.scalars(
            select(AnnouncementModel)
            .where(AnnouncementModel.output_port_id == output_port_id)
            .order_by(desc(AnnouncementModel.created_at))
        ).all()

    def create_announcement(
        self, output_port_id: UUID, request: CreateAnnouncement, actor: User
    ) -> AnnouncementModel:
        announcement = AnnouncementModel(
            output_port_id=output_port_id,
            type=request.type,
            title=request.title,
            message=request.message,
            author_id=actor.id,
        )
        self.db.add(announcement)
        self.db.flush()
        return announcement

    def remove_announcement(
        self, announcement_id: UUID, output_port_id: UUID
    ) -> AnnouncementModel:
        announcement: AnnouncementModel = ensure_exists(
            announcement_id, self.db, AnnouncementModel
        )
        if announcement.output_port_id != output_port_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Required item {announcement_id} does not exist",
            )
        self.db.delete(announcement)
        self.db.flush()
        return announcement
