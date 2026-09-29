from typing import Any
from uuid import uuid4

import pytest

from app.groups.service import GroupService
from tests.factories import (
    GroupFactory,
    MachineUserFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/groups"


@pytest.fixture
def group_payload() -> dict[str, str]:
    return {
        "external_id": "engineering",
        "display_name": "Engineering",
    }


class TestGroupsRouter:
    def test_get_group__returns_group(self, client):
        group = GroupFactory(
            external_id="engineering",
            display_name="Engineering",
        )

        response = client.get(f"{ENDPOINT}/{group.id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": str(group.id),
            "external_id": "engineering",
            "display_name": "Engineering",
        }

    def test_get_group__unknown_id_returns_not_found(self, client):
        response = client.get(f"{ENDPOINT}/{uuid4()}")

        assert response.status_code == 404

    def test_get_group__machine_user_id_returns_not_found(self, client):
        machine_user = MachineUserFactory()

        response = client.get(f"{ENDPOINT}/{machine_user.id}")

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_create_group__creates_group(
        self,
        client,
        group_payload,
    ):
        response = client.post(
            ENDPOINT,
            json=group_payload,
        )

        assert response.status_code == 200
        group_id = response.json()["id"]

        get_response = client.get(f"{ENDPOINT}/{group_id}")

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": group_id,
            **group_payload,
        }

    def test_create_group__without_permission_returns_forbidden(
        self,
        client,
        group_payload,
    ):
        response = client.post(
            ENDPOINT,
            json=group_payload,
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    @pytest.mark.parametrize(
        "payload",
        [
            {"display_name": "Engineering"},
            {"external_id": "engineering"},
            {},
        ],
    )
    def test_create_group__incomplete_payload_is_rejected(
        self,
        client,
        payload: dict[str, Any],
    ):
        response = client.post(ENDPOINT, json=payload)

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_create_group__duplicate_external_id_is_rejected(
        self,
        client,
        group_payload,
    ):
        GroupFactory(external_id=group_payload["external_id"])

        response = client.post(
            ENDPOINT,
            json=group_payload,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "A group with this external ID already exists."
        )
        assert response.json()["correlation_id"]

    @pytest.mark.usefixtures("admin")
    def test_update_group__updates_mutable_fields(self, client):
        group = GroupFactory(
            external_id="engineering",
            display_name="Old name",
        )

        response = client.put(
            f"{ENDPOINT}/{group.id}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 200
        assert response.json() == {"id": str(group.id)}

        get_response = client.get(f"{ENDPOINT}/{group.id}")

        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": str(group.id),
            "external_id": "engineering",
            "display_name": "New name",
        }

    def test_update_group__without_permission_returns_forbidden(
        self,
        client,
    ):
        group = GroupFactory()

        response = client.put(
            f"{ENDPOINT}/{group.id}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_group__missing_display_name_is_rejected(
        self,
        client,
    ):
        group = GroupFactory()

        response = client.put(
            f"{ENDPOINT}/{group.id}",
            json={},
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_update_group__unknown_id_returns_not_found(
        self,
        client,
    ):
        response = client.put(
            f"{ENDPOINT}/{uuid4()}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_delete_group__deletes_group(self, client):
        group = GroupFactory()

        response = client.delete(f"{ENDPOINT}/{group.id}")

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get(f"{ENDPOINT}/{group.id}")
        assert get_response.status_code == 404

    def test_delete_group__without_permission_returns_forbidden(
        self,
        client,
    ):
        group = GroupFactory()

        response = client.delete(f"{ENDPOINT}/{group.id}")

        assert response.status_code == 403
        assert client.get(f"{ENDPOINT}/{group.id}").status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_delete_group__unknown_id_returns_not_found(
        self,
        client,
    ):
        response = client.delete(f"{ENDPOINT}/{uuid4()}")

        assert response.status_code == 404


class TestGroupMembershipRouter:
    @pytest.mark.usefixtures("admin")
    def test_add_group_members(self, client, session):
        group = GroupFactory()
        first = UserFactory()
        second = UserFactory()

        response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(first.id),
                    str(second.id),
                ]
            },
        )

        assert response.status_code == 204
        assert response.content == b""

        service = GroupService(session)
        assert service.has_member(group.id, first.id)
        assert service.has_member(group.id, second.id)

    @pytest.mark.usefixtures("admin")
    def test_add_group_members_ignores_existing_members(
        self,
        client,
        session,
    ):
        group = GroupFactory()
        existing = UserFactory()
        new = UserFactory()

        first_response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(existing.id)]},
        )
        assert first_response.status_code == 204

        response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(existing.id),
                    str(new.id),
                ]
            },
        )

        assert response.status_code == 204
        assert response.content == b""

        service = GroupService(session)
        memberships = service.list_memberships(group.id)

        assert {membership.member_identity_id for membership in memberships} == {
            existing.id,
            new.id,
        }

    def test_add_group_members_requires_permission(self, client):
        group = GroupFactory()
        user = UserFactory()

        response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(user.id)]},
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_add_group_members_rejects_empty_request(self, client):
        group = GroupFactory()

        response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": []},
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_add_group_members_rejects_duplicate_ids(self, client):
        group = GroupFactory()
        user = UserFactory()

        response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(user.id),
                    str(user.id),
                ]
            },
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_remove_group_members(self, client, session):
        group = GroupFactory()
        removed = UserFactory()
        retained = UserFactory()

        setup_response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(removed.id),
                    str(retained.id),
                ]
            },
        )
        assert setup_response.status_code == 204

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(removed.id)]},
        )

        assert response.status_code == 204
        assert response.content == b""

        session.expire_all()
        service = GroupService(session)

        assert not service.has_member(group.id, removed.id)
        assert service.has_member(group.id, retained.id)

    @pytest.mark.usefixtures("admin")
    def test_remove_group_members_ignores_absent_members(
        self,
        client,
        session,
    ):
        group = GroupFactory()
        member = UserFactory()
        absent = UserFactory()

        setup_response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(member.id)]},
        )
        assert setup_response.status_code == 204

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(absent.id)]},
        )

        assert response.status_code == 204
        assert response.content == b""

        session.expire_all()
        assert GroupService(session).has_member(group.id, member.id)

    def test_remove_group_members_requires_permission(self, client):
        group = GroupFactory()
        user = UserFactory()

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(user.id)]},
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_remove_group_members_rejects_empty_request(self, client):
        group = GroupFactory()

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": []},
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_replace_group_members(self, client, session):
        group = GroupFactory()
        retained = UserFactory()
        removed = UserFactory()
        added = UserFactory()

        setup_response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(retained.id),
                    str(removed.id),
                ]
            },
        )
        assert setup_response.status_code == 204

        response = client.put(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(retained.id),
                    str(added.id),
                ]
            },
        )

        assert response.status_code == 204
        assert response.content == b""

        memberships = GroupService(session).list_memberships(group.id)
        assert {membership.member_identity_id for membership in memberships} == {
            retained.id,
            added.id,
        }

    @pytest.mark.usefixtures("admin")
    def test_replace_group_members_rejects_invalid_identity_without_changes(
        self,
        client,
        session,
    ):
        group = GroupFactory()
        existing = UserFactory()

        setup_response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(existing.id)]},
        )
        assert setup_response.status_code == 204

        response = client.put(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(uuid4())]},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "All member identities must exist and be users or machine users."
        )
        assert GroupService(session).has_member(group.id, existing.id)

    def test_replace_group_members_requires_permission(self, client):
        group = GroupFactory()
        user = UserFactory()

        response = client.put(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(user.id)]},
        )

        assert response.status_code == 403
