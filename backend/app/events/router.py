from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.events.service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/latest")
def get_latest_event_timestamp(
    db: Session = Depends(get_db_session),
) -> datetime:
    return EventService(db).get_latest_event_timestamp()
