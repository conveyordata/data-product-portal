from typing import Optional

from pydantic import field_validator

from app.shared.schema import ORMModel


class EnvironmentUpdate(ORMModel):
    is_global: Optional[bool] = None
    position: Optional[int] = None

    @field_validator("is_global")
    @classmethod
    def is_global_not_null(cls, value: Optional[bool]) -> bool:
        if value is None:
            raise ValueError("is_global cannot be null")
        return value
