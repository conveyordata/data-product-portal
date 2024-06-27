from app.environments.schema import Environment
from sqlalchemy.orm import Session
from app.environments.model import Environment as EnvironmentModel


class EnvironmentService:
    def get_environments(self, db: Session) -> list[Environment]:
        return db.query(EnvironmentModel).all()

    def create_environment(self, environment: Environment, db: Session):
        db.add(EnvironmentModel(**environment.model_dump()))
        db.commit()
