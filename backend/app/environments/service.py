from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.environments.enums import PlatformTypes
from app.environments.model import Environment as EnvironmentModel
from app.environments.model import Platform as PlatformModel
from app.environments.schema import CreatePlatform as PlatformSchema
from app.environments.schema import Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> list[Environment]:
        return self.db.query(EnvironmentModel).all()

    def create_environment(self, environment: Environment) -> None:
        self.db.add(EnvironmentModel(**environment.model_dump()))
        self.db.commit()

    def add_or_update_settings(
        self, environment: str, platform_data: PlatformSchema
    ) -> PlatformModel:
        if (
            platform := self.db.query(PlatformModel)
            .filter_by(environment=environment, name=platform_data.name)
            .one_or_none()
        ):
            platform.settings = platform_data.settings.model_dump_json(by_alias=True)
        else:
            platform = PlatformModel(
                name=platform_data.name,
                settings=platform_data.settings.model_dump_json(by_alias=True),
                environment=environment,
            )
            self.db.add(platform)
        self.db.flush()
        return platform

    def delete_settings(self, platform_id: UUID) -> None:
        platform = self.db.get(PlatformModel, str(platform_id))
        if platform:
            platform.delete()
            self.db.flush()

    def get_environment_platforms(
        self, environment: str, platform_name: PlatformTypes | None = None
    ) -> list[PlatformModel] | PlatformModel:
        query = self.db.query(PlatformModel).filter_by(environment=environment)
        if platform_name:
            if not (platform_data := query.filter_by(name=platform_name).first()):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Platform {platform_name.value} not found",
                )
            return platform_data
        else:
            return query.all()
