from pydantic import Field

from app.shared.schema import ORMModel


class ThemeSettings(ORMModel):
    portal_name: str = Field(..., description="Name of the portal")
