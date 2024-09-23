import json

from pydantic import field_validator

from app.shared.schema import ORMModel


class PlatformServiceConfiguration(ORMModel):
    identifiers: list[str]

    @field_validator("identifiers", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v
