from app.core.auth.auth import get_authenticated_user
from app.graph.service import GraphService
from app.users.schema import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.graph.graph import Graph

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("")
def get_graph_data(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Graph:
    return GraphService().get_graph_data(db=db, user=user)
