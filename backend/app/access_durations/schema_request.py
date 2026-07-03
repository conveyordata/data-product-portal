from pydantic import BaseModel, model_validator

from app.access_durations.enums import AccessDurationType


class AccessDurationUpdate(BaseModel):
    access_duration_type: AccessDurationType
    days: int | None = None
    alternative_allowed: bool
    alternative_days: int | None = None

    @model_validator(mode="after")
    def validate_days(self) -> "AccessDurationUpdate":
        if self.access_duration_type == AccessDurationType.TIME_BOUND:
            if self.days is None:
                raise ValueError(
                    "days is required when access_duration_type is time_bound"
                )
        else:
            self.days = None

        if self.alternative_allowed:
            alternative_is_time_bound = (
                self.access_duration_type == AccessDurationType.PERMANENT
            )
            if alternative_is_time_bound and self.alternative_days is None:
                raise ValueError(
                    "alternative_days is required when alternative duration is time_bound"
                )
            if not alternative_is_time_bound:
                self.alternative_days = None
        else:
            self.alternative_days = None

        return self
