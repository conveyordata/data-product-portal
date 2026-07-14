from datetime import datetime, timedelta, timezone

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_ports.input_ports.service import InputPortService
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DatasetFactory,
    InputPortFactory,
    UserFactory,
)


class TestInputPortService:
    def test_get_user_requests(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        dp = DataProductFactory()
        ds = DatasetFactory(data_product=dp)
        pending_recent = InputPortFactory(
            consuming_abstract_data_product=dp,
            dataset=ds,
            request__requested_by=user,
            status=DecisionStatus.PENDING,
        )
        pending_old = InputPortFactory(
            consuming_abstract_data_product=dp,
            dataset=ds,
            request__requested_by=user,
            request__requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            status=DecisionStatus.PENDING,
        )
        approved_old = InputPortFactory(
            consuming_abstract_data_product=dp,
            dataset=ds,
            request__requested_by=user,
            request__requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            status=DecisionStatus.APPROVED,
        )
        requests_old_inactive_hidden = InputPortService(session).get_user_requests(
            user, True
        )
        requests_all = InputPortService(session).get_user_requests(user, False)
        assert len(requests_old_inactive_hidden) == 2
        assert len(requests_all) == 3
        requests_ids = [r.id for r in requests_old_inactive_hidden]
        assert pending_recent.id in requests_ids
        assert pending_old.id in requests_ids
        assert approved_old.id not in requests_ids
