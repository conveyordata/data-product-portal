from pydantic import Field

from app.platforms.schema import Platform
from app.shared.schema import IdNameSchema


class PlatformService(IdNameSchema):
    platform: Platform = Field(
        ..., description="Platform associated with the service configuration"
    )
