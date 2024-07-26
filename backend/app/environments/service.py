from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Query, Session

from app.environments.enums import PlatformTypes
from app.environments.model import Environment as EnvironmentModel
from app.environments.model import Platform as PlatformModel
from app.environments.schema import CreatePlatform, Environment


class EnvironmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_environments(self) -> list[Environment]:
        return self.db.query(EnvironmentModel).all()

    def create_environment(self, environment: Environment) -> None:
        self.db.add(EnvironmentModel(**environment.model_dump()))
        self.db.commit()

    def _get_environment_platforms_query(self, environment: str) -> Query:
        return self.db.query(PlatformModel).filter_by(environment=environment)

    def add_or_update_settings(
        self, environment: str, platform_data: CreatePlatform
    ) -> PlatformModel:
        if (
            platform := self._get_environment_platforms_query(environment)
            .filter_by(name=platform_data.name)
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

    def get_all_environment_platforms(self, environment: str) -> list[PlatformModel]:
        return self._get_environment_platforms_query(environment).all()

    def get_environment_platform(
        self, environment: str, platform_name: PlatformTypes
    ) -> PlatformModel:
        if not (
            platform_data := self._get_environment_platforms_query(environment)
            .filter_by(name=platform_name)
            .first()
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Platform {platform_name.value} not found",
            )
        return platform_data
