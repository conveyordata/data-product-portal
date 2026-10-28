import pytest
from pydantic import ValidationError

from app.configuration.access_durations.enums import AccessDurationType
from app.configuration.access_durations.schema_request import AccessDurationUpdate


class TestAccessDurationUpdateSchema:
    def test_time_bound_with_days_is_valid(self):
        update = AccessDurationUpdate(
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
            alternative_allowed=False,
        )
        assert update.days == 30

    def test_time_bound_without_days_raises(self):
        with pytest.raises(ValidationError, match="days is required"):
            AccessDurationUpdate(
                access_duration_type=AccessDurationType.TIME_BOUND,
                days=None,
                alternative_allowed=False,
            )

    def test_permanent_clears_days(self):
        update = AccessDurationUpdate(
            access_duration_type=AccessDurationType.PERMANENT,
            days=99,
            alternative_allowed=False,
        )
        assert update.days is None

    def test_permanent_with_alternative_time_bound_requires_alternative_days(self):
        with pytest.raises(ValidationError, match="alternative_days is required"):
            AccessDurationUpdate(
                access_duration_type=AccessDurationType.PERMANENT,
                alternative_allowed=True,
                alternative_days=None,
            )

    def test_permanent_with_alternative_time_bound_valid(self):
        update = AccessDurationUpdate(
            access_duration_type=AccessDurationType.PERMANENT,
            alternative_allowed=True,
            alternative_days=30,
        )
        assert update.alternative_days == 30

    def test_time_bound_with_alternative_permanent_clears_alternative_days(self):
        update = AccessDurationUpdate(
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
            alternative_allowed=True,
            alternative_days=99,
        )
        assert update.alternative_days is None

    def test_alternative_not_allowed_clears_alternative_days(self):
        update = AccessDurationUpdate(
            access_duration_type=AccessDurationType.PERMANENT,
            alternative_allowed=False,
            alternative_days=30,
        )
        assert update.alternative_days is None
