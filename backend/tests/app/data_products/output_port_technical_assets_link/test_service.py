from datetime import datetime, timedelta, timezone

from app.authorization.service import AuthorizationService
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.output_port_technical_assets_link.service import (
    TechnicalAssetOutputPortService,
)
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)


class TestDataOutputDatasetService:
    def test_get_user_requests(self, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        dp = DataProductFactory()
        ds = OutputPortFactory(data_product=dp)

        pending_recent = TechnicalAssetOutputPortAssociationFactory(
            output_port=ds, requested_by=user, status=DecisionStatus.PENDING
        )

        pending_old = TechnicalAssetOutputPortAssociationFactory(
            output_port=ds,
            requested_by=user,
            requested_on=datetime.now(timezone.utc) - timedelta(days=60),
            status=DecisionStatus.PENDING,
        )
        approved_old = TechnicalAssetOutputPortAssociationFactory(
            output_port=ds,
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

    def test_get_user_pending_actions__includes_group_inherited_permission(self, session):
        user = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)

        data_product = DataProductFactory()
        output_port = OutputPortFactory(data_product=data_product)
        pending_association = TechnicalAssetOutputPortAssociationFactory(
            output_port=output_port,
            status=DecisionStatus.PENDING,
        )

        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST,
            ],
        )
        DataProductRoleAssignmentFactory(
            identity_id=group.id,
            data_product_id=data_product.id,
            role_id=role.id,
            decision=DecisionStatus.APPROVED,
        )

        # Factories write directly to the database, so synchronize Casbin explicitly.
        AuthorizationService(session).reload_enforcer()
        pending_actions = TechnicalAssetOutputPortService(
            session
        ).get_user_pending_actions(user)

        assert {action.id for action in pending_actions} == {
            pending_association.id
        }
