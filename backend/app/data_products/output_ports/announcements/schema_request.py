from typing import Annotated

from pydantic import Field

from app.data_products.output_ports.announcements.enums import AnnouncementType
from app.shared.schema import NonEmptyStr, ORMModel


class CreateAnnouncement(ORMModel):
    type: AnnouncementType
    title: Annotated[NonEmptyStr, Field(max_length=100)]
    message: Annotated[NonEmptyStr, Field(max_length=2000)]
