from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.groups.service import GroupService
from app.machine_users.schema_request import (
    MachineUserCreate,
    MachineUserUpdate,
)
from app.machine_users.service import MachineUserService
from tests.factories import (
    GroupFactory,
    MachineUserFactory,
)


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

        group_service.add_member(
            group_id=group.id,
            member_identity_id=machine_user.id,
        )
        assert group_service.has_member(group.id, machine_user.id)

        MachineUserService(session).delete_machine_user(machine_user.id)

        assert not group_service.has_member(group.id, machine_user.id)

    def test_delete_machine_user__unknown_id_raises_not_found(
        self,
        session,
    ):
        with pytest.raises(HTTPException) as exc_info:
            MachineUserService(session).delete_machine_user(uuid4())

        assert exc_info.value.status_code == 404