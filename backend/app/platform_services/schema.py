from app.platforms.schema import Platform
from app.shared.schema import IdNameSchema


class PlatformService(IdNameSchema):
    platform: Platform
    template: str
