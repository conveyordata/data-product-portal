from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.core.authz import Authorization
from app.groups.service import GroupService
from app.machine_users.model import MachineUser
from app.machine_users.schema_request import (
    MachineUserCreate,
    MachineUserUpdate,
)
from app.machine_users.service import MachineUserService
from tests.factories import (
    GroupFactory,
    MachineUserFactory,
    UserFactory,
)
from tests.groups_util import group_has_member


class TestMachineUserService:
    def test_get_machine_user__returns_machine_user(self, session):
        machine_user = MachineUserFactory(
            external_id="automation",
            display_name="Automation",
        )

        result = MachineUserService(session).get_machine_user(
            machine_user.id,
        )

        assert result.id == machine_user.id
        assert result.external_id == "automation"
        assert result.display_name == "Automation"

    def test_get_machine_user__unknown_id_raises_not_found(self, session):
        with pytest.raises(HTTPException) as exc_info:
            MachineUserService(session).get_machine_user(uuid4())

        assert exc_info.value.status_code == 404

    def test_get_machine_user__group_id_raises_not_found(self, session):
        group = GroupFactory()

        with pytest.raises(HTTPException) as exc_info:
            MachineUserService(session).get_machine_user(group.id)

        assert exc_info.value.status_code == 404

    def test_create_machine_user__creates_machine_user(self, session):
        service = MachineUserService(session)

        result = service.create_machine_user(
            MachineUserCreate(
                external_id="deployment-agent",
                display_name="Deployment Agent",
            )
        )

        machine_user = service.get_machine_user(result.id)
        assert machine_user.external_id == "deployment-agent"
        assert machine_user.display_name == "Deployment Agent"

    def test_create_machine_user__duplicate_external_id_is_rejected(
        self,
        session,
    ):
        MachineUserFactory(external_id="deployment-agent")
        service = MachineUserService(session)

        with pytest.raises(HTTPException) as exc_info:
            service.create_machine_user(
                MachineUserCreate(
                    external_id="deployment-agent",
                    display_name="Another Deployment Agent",
                )
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == (
            "A machine user with this external ID already exists."
        )

    def test_update_machine_user__updates_display_name(self, session):
        machine_user = MachineUserFactory(
            external_id="deployment-agent",
            display_name="Old name",
        )
        service = MachineUserService(session)

        result = service.update_machine_user(
            machine_user.id,
            MachineUserUpdate(display_name="New name"),
        )

        session.refresh(machine_user)
        assert result.id == machine_user.id
        assert machine_user.external_id == "deployment-agent"
        assert machine_user.display_name == "New name"

    def test_update_machine_user__unknown_id_raises_not_found(
        self,
        session,
    ):
        with pytest.raises(HTTPException) as exc_info:
            MachineUserService(session).update_machine_user(
                uuid4(),
                MachineUserUpdate(display_name="New name"),
            )

        assert exc_info.value.status_code == 404

    def test_delete_machine_user__deletes_machine_user(self, session):
        machine_user = MachineUserFactory()
        machine_user_id = machine_user.id
        service = MachineUserService(session)

        service.delete_machine_user(machine_user_id)

        with pytest.raises(HTTPException) as exc_info:
            service.get_machine_user(machine_user_id)

        assert exc_info.value.status_code == 404

    def test_delete_machine_user__deletes_group_memberships(
        self,
        session,
    ):
        group = GroupFactory()
        machine_user = MachineUserFactory()
        group_service = GroupService(session)

        group_service.add_members(
            group_id=group.id,
            member_identity_ids=[machine_user.id],
        )
        assert group_has_member(session, group.id, machine_user.id)

        MachineUserService(session).delete_machine_user(machine_user.id)

        assert not group_has_member(session, group.id, machine_user.id)

    def test_delete_machine_user__unknown_id_raises_not_found(
        self,
        session,
    ):
        with pytest.raises(HTTPException) as exc_info:
            MachineUserService(session).delete_machine_user(uuid4())

        assert exc_info.value.status_code == 404

    def test_create_machine_users_batch__creates_all_valid_items(self, session):
        result = MachineUserService(session).create_machine_users_batch(
            [
                {
                    "external_id": "deployment-agent",
                    "display_name": "Deployment Agent",
                },
                {
                    "external_id": "monitoring-agent",
                    "display_name": "Monitoring Agent",
                },
            ]
        )

        machine_users = session.scalars(
            select(MachineUser).where(MachineUser.id.in_(result.ids))
        ).all()

        assert len(result.ids) == 2
        assert result.errors == []
        assert {machine_user.external_id for machine_user in machine_users} == {
            "deployment-agent",
            "monitoring-agent",
        }

    def test_create_machine_users_batch__skips_schema_invalid_items(self, session):
        invalid_item = {
            "external_id": "",
            "display_name": "",
        }

        result = MachineUserService(session).create_machine_users_batch(
            [
                {
                    "external_id": "deployment-agent",
                    "display_name": "Deployment Agent",
                },
                invalid_item,
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].item == invalid_item
        assert len(result.errors[0].errors) == 2

    def test_create_machine_users_batch__skips_existing_external_id(self, session):
        MachineUserFactory(external_id="existing-agent")

        result = MachineUserService(session).create_machine_users_batch(
            [
                {
                    "external_id": "existing-agent",
                    "display_name": "Existing Agent",
                },
                {
                    "external_id": "new-agent",
                    "display_name": "New Agent",
                },
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].errors == [
            "A machine user with this external ID already exists."
        ]

        created = session.get(MachineUser, result.ids[0])
        assert created is not None
        assert created.external_id == "new-agent"

    def test_create_machine_users_batch__rejects_later_request_duplicate(self, session):
        result = MachineUserService(session).create_machine_users_batch(
            [
                {
                    "external_id": "duplicate-agent",
                    "display_name": "First",
                },
                {
                    "external_id": "duplicate-agent",
                    "display_name": "Second",
                },
            ]
        )

        assert len(result.ids) == 1
        assert len(result.errors) == 1
        assert result.errors[0].errors == [
            "A machine user with this external ID already exists."
        ]

        created = session.get(MachineUser, result.ids[0])
        assert created is not None
        assert created.display_name == "First"

    def test_delete_machine_users_batch__deletes_matching_machine_users(self, session):
        first = MachineUserFactory()
        second = MachineUserFactory()
        retained = MachineUserFactory()

        MachineUserService(session).delete_machine_users_batch([first.id, second.id])

        assert session.get(MachineUser, first.id) is None
        assert session.get(MachineUser, second.id) is None
        assert session.get(MachineUser, retained.id) is not None

    def test_delete_machine_users_batch__ignores_unknown_and_wrong_type_ids(
        self, session
    ):
        machine_user = MachineUserFactory()
        user = UserFactory()

        MachineUserService(session).delete_machine_users_batch(
            [machine_user.id, user.id, uuid4()]
        )

        assert session.get(MachineUser, machine_user.id) is None
        assert user in session

    def test_delete_machine_users_batch__clears_only_deleted_authorization(
        self,
        authorizer: Authorization,
        session,
    ):
        removed = MachineUserFactory()
        retained = MachineUserFactory()

        authorizer.assign_resource_role(
            user_id=removed.id,
            role_id="resource-role",
            resource_id="resource",
        )
        authorizer.assign_domain_role(
            user_id=removed.id,
            role_id="domain-role",
            domain_id="domain",
        )
        authorizer.assign_global_role(
            user_id=removed.id,
            role_id="global-role",
        )
        authorizer.assign_global_role(
            user_id=retained.id,
            role_id="retained-role",
        )

        MachineUserService(session).delete_machine_users_batch([removed.id])

        assert not authorizer.has_resource_role(
            user_id=removed.id,
            role_id="resource-role",
            resource_id="resource",
        )
        assert not authorizer.has_domain_role(
            user_id=removed.id,
            role_id="domain-role",
            domain_id="domain",
        )
        assert not authorizer.has_global_role(
            user_id=removed.id,
            role_id="global-role",
        )
        assert authorizer.has_global_role(
            user_id=retained.id,
            role_id="retained-role",
        )
