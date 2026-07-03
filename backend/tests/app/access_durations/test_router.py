import pytest
from pydantic import ValidationError

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.access_durations.schema_request import AccessDurationUpdate
from tests.factories import AccessDurationFactory

ENDPOINT = "/api/v2/access_durations"


# ---------------------------------------------------------------------------
# Schema validation unit tests
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------

PERMANENT_PAYLOAD = {
    "access_duration_type": "permanent",
    "days": None,
    "alternative_allowed": False,
    "alternative_days": None,
}

TIME_BOUND_PAYLOAD = {
    "access_duration_type": "time_bound",
    "days": 30,
    "alternative_allowed": False,
    "alternative_days": None,
}


class TestAccessDurationsRouter:
    def test_get_all_returns_all_durations(self, client):
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.PERMANENT,
            is_default=True,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.EXPLORATION,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
            is_default=True,
        )
        response = client.get(ENDPOINT)
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_default_returns_default_row(self, client):
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=14,
            is_default=True,
        )
        response = client.get(f"{ENDPOINT}/data_products/default")
        assert response.status_code == 200
        data = response.json()
        assert data["access_duration_type"] == "time_bound"
        assert data["days"] == 14
        assert data["is_default"] is True

    def test_get_default_not_found(self, client):
        response = client.get(f"{ENDPOINT}/data_products/default")
        assert response.status_code == 404

    def test_update_requires_admin(self, client):
        response = client.put(f"{ENDPOINT}/data_products", json=PERMANENT_PAYLOAD)
        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_sets_permanent_default(self, client):
        response = client.put(f"{ENDPOINT}/data_products", json=PERMANENT_PAYLOAD)
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["access_duration_type"] == "permanent"
        assert rows[0]["days"] is None
        assert rows[0]["is_default"] is True

    @pytest.mark.usefixtures("admin")
    def test_update_sets_time_bound_default_with_days(self, client):
        response = client.put(f"{ENDPOINT}/data_products", json=TIME_BOUND_PAYLOAD)
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 1
        assert rows[0]["access_duration_type"] == "time_bound"
        assert rows[0]["days"] == 30
        assert rows[0]["is_default"] is True

    @pytest.mark.usefixtures("admin")
    def test_update_time_bound_without_days_returns_422(self, client):
        response = client.put(
            f"{ENDPOINT}/data_products",
            json={
                "access_duration_type": "time_bound",
                "days": None,
                "alternative_allowed": False,
            },
        )
        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_update_with_alternative_creates_two_rows(self, client):
        payload = {
            "access_duration_type": "time_bound",
            "days": 30,
            "alternative_allowed": True,
            "alternative_days": None,
        }
        response = client.put(f"{ENDPOINT}/data_products", json=payload)
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 2
        defaults = [r for r in rows if r["is_default"]]
        alternatives = [r for r in rows if not r["is_default"]]
        assert len(defaults) == 1
        assert defaults[0]["access_duration_type"] == "time_bound"
        assert len(alternatives) == 1
        assert alternatives[0]["access_duration_type"] == "permanent"
        assert alternatives[0]["days"] is None

    @pytest.mark.usefixtures("admin")
    def test_update_permanent_with_time_bound_alternative(self, client):
        payload = {
            "access_duration_type": "permanent",
            "days": None,
            "alternative_allowed": True,
            "alternative_days": 14,
        }
        response = client.put(f"{ENDPOINT}/data_products", json=payload)
        assert response.status_code == 200
        rows = response.json()
        assert len(rows) == 2
        alt = next(r for r in rows if not r["is_default"])
        assert alt["access_duration_type"] == "time_bound"
        assert alt["days"] == 14

    @pytest.mark.usefixtures("admin")
    def test_update_removing_alternative_leaves_one_row(self, client):
        # Seed with two rows
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.TIME_BOUND,
            days=30,
            is_default=True,
        )
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.DATA_PRODUCT,
            access_duration_type=AccessDurationType.PERMANENT,
            days=None,
            is_default=False,
        )
        response = client.put(f"{ENDPOINT}/data_products", json=TIME_BOUND_PAYLOAD)
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.usefixtures("admin")
    def test_update_only_affects_given_product_type(self, client):
        AccessDurationFactory(
            abstract_data_product_type=AbstractDataProductType.EXPLORATION,
            access_duration_type=AccessDurationType.PERMANENT,
            is_default=True,
        )
        client.put(f"{ENDPOINT}/data_products", json=TIME_BOUND_PAYLOAD)
        # Exploration row must be untouched
        response = client.get(f"{ENDPOINT}/explorations/default")
        assert response.status_code == 200
        assert response.json()["access_duration_type"] == "permanent"
