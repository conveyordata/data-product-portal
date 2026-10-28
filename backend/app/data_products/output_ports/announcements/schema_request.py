from typing import Annotated, Optional

from pydantic import AfterValidator, Field, HttpUrl

from app.data_products.output_ports.announcements.enums import AnnouncementType
from app.shared.schema import NonEmptyStr, ORMModel


class CreateAnnouncement(ORMModel):
    type: AnnouncementType
    title: Annotated[NonEmptyStr, Field(max_length=100)]
    message: Annotated[NonEmptyStr, Field(max_length=2000)]
    link: Annotated[Optional[HttpUrl], AfterValidator(lambda url: url and str(url))] = (
        None
    )
