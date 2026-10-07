from uuid import uuid4

import pytest

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignment,
)
from app.authorization.roles.schema import Scope
from app.core.authz import REDACTION_VALUE
from app.core.authz.actions import AuthorizationAction
from app.data_products.model import DataProductVisibility
from app.events.enums import EventReferenceEntity
from app.events.model import Event
from app.events.schema_response import GetEventHistoryResponseItemOld
from app.settings import settings
from app.users.model import User
from tests.app.data_products.output_port_technical_assets_link.test_router import (
    TECHNICAL_ASSETS_OUTPUT_PORTS_ENDPOINT,
)
from tests.factories import (
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    EventFactory,
    GlobalRoleAssignmentFactory,
    GroupFactory,
    GroupMembershipFactory,
    InputPortFactory,
    OutputPortFactory,
    RoleFactory,
    TechnicalAssetFactory,
    TechnicalAssetOutputPortAssociationFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/users"


class TestUsersRouter:
    def test_get_users(self, client):
        UserFactory()

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_remove_user_not_admin(self, client):
        user = UserFactory()

        response = client.delete(f"{ENDPOINT}/{user.id}")
        assert response.status_code == 403

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()["users"]) == 2

    @pytest.mark.usefixtures("admin")
    def test_remove_user(self, client):
        user = UserFactory()

        response = client.get(f"{ENDPOINT}")
        response = client.delete(f"{ENDPOINT}/{user.id}")
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()["users"]) == 1

    @pytest.mark.usefixtures("admin")
    def test_remove_user__preserves_event_references(self, client, session):
        user = UserFactory()
        other_user = UserFactory()
        actor_event = EventFactory(actor=user)
        subject_event = EventFactory(
            actor=other_user,
            subject_id=user.id,
            subject_type=EventReferenceEntity.USER,
            deleted_subject_identifier=None,
        )
        target_event = EventFactory(
            actor=other_user,
            target_id=user.id,
            target_type=EventReferenceEntity.USER,
        )
        user_id, email = user.id, user.email
        actor_event_id = actor_event.id
        subject_event_id = subject_event.id
        target_event_id = target_event.id

        response = client.delete(f"{ENDPOINT}/{user_id}")

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(User, user_id) is None
        actor_event = session.get(Event, actor_event_id)
        assert actor_event is not None
        assert actor_event.actor_id == user_id
        assert actor_event.actor is None
        assert actor_event.deleted_actor_identifier == email
        history = GetEventHistoryResponseItemOld.model_validate(actor_event).convert()
        assert history.actor is None
        assert history.deleted_actor_identifier == email
        subject_event = session.get(Event, subject_event_id)
        assert subject_event.deleted_subject_identifier == email
        assert subject_event.user is None
        target_event = session.get(Event, target_event_id)
        assert target_event.deleted_target_identifier == email
        assert target_event.user is None

    @pytest.mark.usefixtures("admin")
    def test_remove_user__clears_authorization(self, client, authorizer, session):
        user = UserFactory()
        other_user = UserFactory()
        group = GroupFactory()
        GroupMembershipFactory(group=group, member=user)
        user_id = user.id
        group_id = group.id
        authorizer.assign_resource_role(
            user_id=user_id, role_id="resource-role", resource_id="resource"
        )
        authorizer.assign_domain_role(
            user_id=user_id, role_id="domain-role", domain_id="domain"
        )
        authorizer.assign_global_role(user_id=user_id, role_id="global-role")
        authorizer.assign_resource_group_membership(
            member_identity_id=user_id, group_id=group_id
        )
        authorizer.assign_global_group_membership(
            member_identity_id=user_id, group_id=group_id
        )
        authorizer.assign_global_role(user_id=other_user.id, role_id="global-role")

        response = client.delete(f"{ENDPOINT}/{user_id}")

        assert response.status_code == 200, response.text
        assert not authorizer.has_resource_role(
            user_id=user_id, role_id="resource-role", resource_id="resource"
        )
        assert not authorizer.has_domain_role(
            user_id=user_id, role_id="domain-role", domain_id="domain"
        )
        assert not authorizer.has_global_role(user_id=user_id, role_id="global-role")
        assert not authorizer.has_resource_role(
            user_id=user_id, role_id=group_id, resource_id="*"
        )
        assert not authorizer.has_global_role(user_id=user_id, role_id=group_id)
        assert authorizer.has_global_role(user_id=other_user.id, role_id="global-role")

    @pytest.mark.usefixtures("admin")
    def test_remove_user__with_data_product_role(self, client, session):
        user = UserFactory()
        data_product = DataProductFactory()
        role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])
        assignment = DataProductRoleAssignmentFactory(
            identity_id=user.id,
            data_product_id=data_product.id,
            role_id=role.id,
        )

        # stored for later comparison
        user_id = user.id
        assignment_id = assignment.id
        response = client.delete(f"{ENDPOINT}/{user_id}")

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(User, user_id) is None
        assert session.get(DataProductRoleAssignment, assignment_id) is None

    @pytest.mark.usefixtures("admin")
    def test_remove_user__with_dataset_role(self, client, session):
        user = UserFactory()
        output_port = OutputPortFactory()
        role = RoleFactory(scope=Scope.DATASET, permissions=[])
        assignment = DatasetRoleAssignmentFactory(
            user_id=user.id,
            output_port=output_port,
            role_id=role.id,
        )

        # stored for later comparison
        user_id = user.id
        assignment_id = assignment.id
        response = client.delete(f"{ENDPOINT}/{user_id}")

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(User, user_id) is None
        assert session.get(DatasetRoleAssignment, assignment_id) is None

    @pytest.mark.usefixtures("admin")
    def test_remove_user__with_data_product_and_dataset_roles(self, client, session):
        user = UserFactory()

        data_product = DataProductFactory()
        data_product_role = RoleFactory(scope=Scope.DATA_PRODUCT, permissions=[])
        data_product_assignment = DataProductRoleAssignmentFactory(
            identity_id=user.id,
            data_product_id=data_product.id,
            role_id=data_product_role.id,
        )

        output_port = OutputPortFactory()
        dataset_role = RoleFactory(scope=Scope.DATASET, permissions=[])
        dataset_assignment = DatasetRoleAssignmentFactory(
            user_id=user.id,
            output_port=output_port,
            role_id=dataset_role.id,
        )

        # stored for later comparison
        user_id = user.id
        data_product_assignment_id = data_product_assignment.id
        dataset_assignment_id = dataset_assignment.id
        response = client.delete(f"{ENDPOINT}/{user_id}")

        assert response.status_code == 200, response.text
        session.expire_all()
        assert session.get(User, user_id) is None
        assert (
            session.get(DataProductRoleAssignment, data_product_assignment_id) is None
        )
        assert session.get(DatasetRoleAssignment, dataset_assignment_id) is None

    def test_post_user_not_admin(self, client):
        response = client.post(f"{ENDPOINT}")
        assert response.status_code == 403

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()["users"]) == 1

    @pytest.mark.usefixtures("admin")
    def test_post_user(self, client):
        response = client.post(
            f"{ENDPOINT}",
            json={
                "email": "test@user.com",
                "external_id": "test-user",
                "first_name": "test",
                "last_name": "user",
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()["users"]) == 2

    def test_post_has_seen_tour(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()["users"]) == 1
        assert response.json()["users"][0]["has_seen_tour"] is False
        response = client.post(f"{ENDPOINT}/current/seen_tour")
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()["users"]) == 1
        assert response.json()["users"][0]["has_seen_tour"] is True
        assert response.status_code == 200

    def test_post_has_seen_tour_v2(self, client):
        UserFactory(external_id=settings.DEFAULT_USERNAME)
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()["users"]) == 1
        assert response.json()["users"][0]["has_seen_tour"] is False
        response = client.post("/api/v2/users/current/seen_tour")
        response = client.get(f"{ENDPOINT}")
        assert len(response.json()["users"]) == 1
        assert response.json()["users"][0]["has_seen_tour"] is True
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_post_user_default_admin(self, client):
        response = client.post(
            f"{ENDPOINT}",
            json={
                "email": "test@user.com",
                "external_id": "test-user",
                "first_name": "test",
                "last_name": "user",
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        assert response.status_code == 200
        assert len(response.json()["users"]) == 2

    def test_can_become_admin_not_admin(self, client):
        user = UserFactory(
            external_id=settings.DEFAULT_USERNAME, can_become_admin=False
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": True,
            },
        )
        assert response.status_code == 403

    def test_can_unbecome_admin(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=True)
        UserFactory(can_become_admin=True)
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": False,
            },
        )
        assert response.status_code == 200
        response = client.get(f"{ENDPOINT}")
        data = response.json()["users"]
        for user_data in data:
            if user_data["id"] == str(user.id):
                assert user_data["can_become_admin"] is False

    def test_can_not_unbecome_admin_latest_admin(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME, can_become_admin=True)
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": False,
            },
        )
        assert response.status_code == 400
        response = client.get(f"{ENDPOINT}")
        data = response.json()["users"]
        for user_data in data:
            if user_data["id"] == str(user.id):
                assert user_data["can_become_admin"] is True

    def test_can_become_admin(self, client):
        user = UserFactory(
            external_id=settings.DEFAULT_USERNAME, can_become_admin=False
        )
        role = RoleFactory(
            scope=Scope.GLOBAL, permissions=[AuthorizationAction.GLOBAL__CREATE_USER]
        )
        GlobalRoleAssignmentFactory(
            identity_id=user.id,
            role_id=role.id,
        )
        response = client.put(
            f"{ENDPOINT}/set_can_become_admin",
            json={
                "user_id": str(user.id),
                "can_become_admin": True,
            },
        )
        assert response.status_code == 200

        response = client.get(f"{ENDPOINT}")
        data = response.json()["users"]
        for user_data in data:
            if user_data["id"] == str(user.id):
                assert user_data["can_become_admin"] is True

    def test_get_pending_actions_no_action(self, client):
        ds = OutputPortFactory()
        TechnicalAssetOutputPortAssociationFactory(output_port=ds)
        response = client.get("/api/v2/users/current/pending_actions")
        assert response.json() == {"pending_actions": []}

    def test_get_pending_actions_input_port(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        input_port = InputPortFactory(status=DecisionStatus.PENDING)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=input_port.output_port.id
        )

        response = client.get("/api/v2/users/current/pending_actions")
        assert response.status_code == 200, response.text
        assert len(response.json()["pending_actions"]) == 1
        assert not response.json()["pending_actions"][0]["input_port"][
            "consuming_abstract_data_product"
        ]["is_redacted"]
        assert (
            response.json()["pending_actions"][0]["input_port"][
                "consuming_abstract_data_product"
            ]["name"]
            != REDACTION_VALUE
        )

    def test_get_pending_actions_input_port_redacted(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        input_port = InputPortFactory(
            status=DecisionStatus.PENDING,
            consuming_abstract_data_product=DataProductFactory(
                visibility=DataProductVisibility.HIDDEN
            ),
        )
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                AuthorizationAction.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=input_port.output_port.id
        )

        response = client.get("/api/v2/users/current/pending_actions")
        assert response.status_code == 200, response.text
        assert len(response.json()["pending_actions"]) == 1
        assert response.json()["pending_actions"][0]["input_port"][
            "consuming_abstract_data_product"
        ]["is_redacted"]
        assert (
            response.json()["pending_actions"][0]["input_port"][
                "consuming_abstract_data_product"
            ]["name"]
            == REDACTION_VALUE
        )

    def test_get_pending_actions(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        technical_asset = TechnicalAssetFactory(owner=data_product)
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[
                AuthorizationAction.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK
            ],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )

        ds = OutputPortFactory(data_product=data_product)
        role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[
                AuthorizationAction.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST
            ],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=role.id, output_port_id=ds.id
        )

        response = client.post(
            f"{TECHNICAL_ASSETS_OUTPUT_PORTS_ENDPOINT.format(data_product.id, ds.id)}/add",
            json={"technical_asset_id": f"{technical_asset.id}"},
        )
        assert response.status_code == 200
        response = client.get("/api/v2/users/current/pending_actions")
        assert response.json()["pending_actions"][0]["technical_asset_id"] == str(
            technical_asset.id
        )
        assert response.json()["pending_actions"][0]["status"] == "pending"

    def test_get_current_user(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        response = client.get("/api/v2/users/current")
        assert response.status_code == 200, response.text
        assert response.json()["id"] == str(user.id)

    def test_get_current_user_my_requests(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        InputPortFactory(request__requested_by=user)
        response = client.get("/api/v2/users/current/my_requests")
        assert response.status_code == 200, response.text
        assert len(response.json()["my_requests"]) == 1

    def test_get_current_user_my_requests_redacted(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        InputPortFactory(
            request__requested_by=user,
            consuming_abstract_data_product=DataProductFactory(
                visibility=DataProductVisibility.HIDDEN
            ),
        )
        response = client.get("/api/v2/users/current/my_requests")
        assert response.status_code == 200, response.text
        assert len(response.json()["my_requests"]) == 1
        assert (
            response.json()["my_requests"][0]["input_port"][
                "consuming_abstract_data_product"
            ]["name"]
            == REDACTION_VALUE
        )

    def test_get_user_groups__returns_groups(self, client):
        user = UserFactory()
        first = GroupFactory(
            external_id="engineering",
            display_name="Engineering",
        )
        second = GroupFactory(
            external_id="finance",
            display_name="Finance",
        )
        unrelated = GroupFactory()

        GroupMembershipFactory(group=second, member=user)
        GroupMembershipFactory(group=first, member=user)

        response = client.get(f"{ENDPOINT}/{user.id}/groups")

        assert response.status_code == 200
        assert response.json() == {
            "groups": [
                {
                    "id": str(first.id),
                    "external_id": first.external_id,
                    "display_name": first.display_name,
                },
                {
                    "id": str(second.id),
                    "external_id": second.external_id,
                    "display_name": second.display_name,
                },
            ]
        }
        assert str(unrelated.id) not in response.text

    def test_get_user_groups__user_without_groups_returns_empty_list(self, client):
        user = UserFactory()

        response = client.get(f"{ENDPOINT}/{user.id}/groups")

        assert response.status_code == 200
        assert response.json() == {"groups": []}

    def test_get_user_groups__unknown_user_returns_not_found(self, client):
        response = client.get(f"{ENDPOINT}/{uuid4()}/groups")

        assert response.status_code == 404

    def test_get_current_user_groups__returns_authenticated_users_groups(self, client):
        authenticated_user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        other_user = UserFactory()

        expected_group = GroupFactory(
            external_id="engineering",
            display_name="Engineering",
        )
        other_group = GroupFactory()

        GroupMembershipFactory(group=expected_group, member=authenticated_user)
        GroupMembershipFactory(group=other_group, member=other_user)

        response = client.get(f"{ENDPOINT}/current/groups")

        assert response.status_code == 200
        assert response.json() == {
            "groups": [
                {
                    "id": str(expected_group.id),
                    "external_id": expected_group.external_id,
                    "display_name": expected_group.display_name,
                }
            ]
        }
