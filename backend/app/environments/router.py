from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.environments.schema import Environment
from app.environments.service import EnvironmentService

router = APIRouter(prefix="/envs", tags=["environments"])


@router.get("")
def get_environments(db: Session = Depends(get_db_session)) -> list[Environment]:
    envs = EnvironmentService().get_environments(db)
    breakpoint()
    return envs


@router.post("")
def create_environment(environment: Environment, db: Session = Depends(get_db_session)):
    return EnvironmentService().create_environment(environment, db)
