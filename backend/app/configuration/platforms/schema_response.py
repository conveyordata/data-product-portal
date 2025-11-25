from typing import Sequence

from app.shared.schema import IdNameSchema, ORMModel


class Platform(IdNameSchema):
    pass


class GetAllPlatformsResponse(ORMModel):
    platforms: Sequence[Platform]
