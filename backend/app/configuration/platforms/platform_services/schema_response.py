from typing import Sequence

from app.configuration.platforms.platform_services.schema import PlatformService
from app.shared.schema import ORMModel


class GetPlatformServicesResponse(ORMModel):
    platform_services: Sequence[PlatformService]
