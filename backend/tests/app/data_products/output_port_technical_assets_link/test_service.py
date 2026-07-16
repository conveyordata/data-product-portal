from datetime import datetime, timedelta, timezone

from app.authorization.role_assignments.enums import DecisionStatus
from app.data_products.output_port_technical_assets_link.service import (
    TechnicalAssetOutputPortService,
)
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    OutputPortFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)


class TestDataOutputDatasetService:
    def test_get_user_requests(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        dp = DataProductFactory()
        ds = OutputPortFactory(data_product=dp)

        pending_recent = TechnicalAssetOutputPortAssociationFactory(
            dataset=ds, requested_by=user, status=DecisionStatus.PENDING
        )

        pending_old = TechnicalAssetOutputPortAssociationFactory(
            dataset=ds,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            status=DecisionStatus.PENDING,
        )
        approved_old = TechnicalAssetOutputPortAssociationFactory(
            dataset=ds,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            status=DecisionStatus.APPROVED,
        )
        requests_old_inactive_hidden = TechnicalAssetOutputPortService(
            session
        ).get_user_requests(user, True)
        requests_all = TechnicalAssetOutputPortService(session).get_user_requests(
            user, False
        )
        assert len(requests_old_inactive_hidden) == 2
        assert len(requests_all) == 3
        requests_ids = [r.id for r in requests_old_inactive_hidden]
        assert pending_recent.id in requests_ids
        assert pending_old.id in requests_ids
        assert approved_old.id not in requests_ids
