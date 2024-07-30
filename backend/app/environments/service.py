from sqlalchemy.orm import Session

from app.environments.model import Environment as EnvironmentModel
from app.environments.schema import Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> list[Environment]:
        return self.db.query(EnvironmentModel).all()

    def create_environment(self, environment: Environment) -> None:
        self.db.add(EnvironmentModel(**environment.model_dump()))
        self.db.commit()
