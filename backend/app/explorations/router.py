from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.explorations.schema_request import CreateExplorationRequest
from app.explorations.schema_response import (
    CreateExplorationResponse,
    GetExplorationsResponse,
)
from app.explorations.service import ExplorationService

route = "/v2/explorations"
router = APIRouter(tags=["Explorations"], prefix=route)


@router.get("", response_model=GetExplorationsResponse)
def get_explorations(
    db: Session = Depends(get_db_session),
    # filter_to_user_with_assigment: Optional[UUID] = Query(default=None),
):
    return {"explorations": ExplorationService(db).get_explorations()}


@router.post("", response_model=CreateExplorationResponse)
def create_exploration(
    exploration: CreateExplorationRequest,
    db: Session = Depends(get_db_session),
):
    return ExplorationService(db).create_exploration(exploration)
