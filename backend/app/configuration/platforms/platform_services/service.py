from typing import Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.platform_service_configurations.model import (
    PlatformServiceConfiguration,
)
from app.configuration.platforms.model import Platform
from app.configuration.platforms.platform_services.model import (
    PlatformService as PlatformServiceModel,
)
from app.configuration.platforms.platform_services.schema import PlatformService
from app.database.deps import get_db_session
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class PlatformServiceService:
    def __init__(self, db: Session = Depends(get_db_session, scope="function")):
        self.db = db

    def get_platform_services(self, platform_id: UUID) -> Sequence[PlatformService]:
        return self.db.scalars(
            select(PlatformServiceModel).filter_by(platform_id=platform_id)
        ).all()

    def ensure_for_plugins(self, plugins: Sequence[type[TechnicalAssetPlugin]]) -> None:
        self.db.execute(select(func.pg_advisory_xact_lock(func.hashtext("platforms"))))
        for plugin in plugins:
            metadata = plugin.get_platform_metadata()
            if metadata.result_string_template is None:
                continue

            service = self.db.scalar(
                select(PlatformServiceModel).where(
                    func.lower(PlatformServiceModel.name) == metadata.platform_key
                )
            )
            if service is None:
                platform = self._platform(
                    metadata.parent_platform or metadata.platform_key
                )
                service = PlatformServiceModel(
                    name=metadata.platform_key, platform=platform
                )
                self.db.add(service)
                self.db.flush()

            service.result_string_template = metadata.result_string_template
            service.technical_info_template = (
                metadata.technical_info_template or metadata.result_string_template
            )
            has_options = self.db.scalar(
                select(PlatformServiceConfiguration).filter_by(service_id=service.id)
            )
            if not has_options:
                self.db.add(
                    PlatformServiceConfiguration(
                        platform_id=service.platform_id,
                        service_id=service.id,
                        config="[]",
                    )
                )

    def _platform(self, name: str) -> Platform:
        platform = self.db.scalar(
            select(Platform).where(func.lower(Platform.name) == name)
        )
        return platform or Platform(name=name)
