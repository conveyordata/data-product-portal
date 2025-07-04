from app.platforms.schema import Platform
from app.shared.schema import IdNameSchema


class PlatformService(IdNameSchema):
    platform: Platform
    result_string_template: str
    technical_info_template: str
