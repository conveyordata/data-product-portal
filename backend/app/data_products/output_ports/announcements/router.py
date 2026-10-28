from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, OutputPortResolver
from app.data_products.output_ports.announcements.schema_request import (
    CreateAnnouncement,
)
from app.data_products.output_ports.announcements.schema_response import (
    CreateAnnouncementResponse,
    GetAnnouncementsResponse,
)
from app.data_products.output_ports.announcements.service import AnnouncementService
from app.data_products.output_ports.model import ensure_output_port_exists
from app.database.deps import get_db_session
from app.events.enums import EventEntityType, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.users.model import User

router = APIRouter(prefix="/{id}/announcements")


@router.get(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN__OUTPUT_PORT__READ_ANNOUNCEMENTS, OutputPortResolver
            )
        )
    ],
)
def get_output_port_announcements(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
) -> GetAnnouncementsResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return GetAnnouncementsResponse(
        announcements=AnnouncementService(db).get_announcements(ds.id)
    )


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, OutputPortResolver
            )
        )
    ],
)
def create_output_port_announcement(
    data_product_id: UUID,
    id: UUID,
    request: CreateAnnouncement,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateAnnouncementResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    announcement = AnnouncementService(db).create_announcement(
        ds.id, request, authenticated_user
    )
    EventService(db).create_event(
        CreateEvent(
            name=EventType.ANNOUNCEMENT_CREATED,
            subject_id=ds.id,
            subject_type=EventEntityType.OUTPUT_PORT,
            target_id=announcement.id,
            target_type=EventEntityType.ANNOUNCEMENT,
            actor_id=authenticated_user.id,
        )
    )
    return CreateAnnouncementResponse(id=announcement.id)


@router.delete(
    "/{announcement_id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, OutputPortResolver
            )
        )
    ],
)
def remove_output_port_announcement(
    data_product_id: UUID,
    id: UUID,
    announcement_id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    announcement = AnnouncementService(db).remove_announcement(announcement_id, ds.id)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.ANNOUNCEMENT_REMOVED,
            subject_id=ds.id,
            subject_type=EventEntityType.OUTPUT_PORT,
            target_id=announcement.id,
            target_type=EventEntityType.ANNOUNCEMENT,
            deleted_target_identifier=announcement.title,
            actor_id=authenticated_user.id,
        )
    )
