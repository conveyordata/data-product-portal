import asyncio
from typing import Any
from uuid import uuid4

import pytest

from app.groups.router import _serialize_group_members_replacement
from app.groups.service import GroupService
from app.settings import settings
from tests.factories import (
    GroupFactory,
    GroupMembershipFactory,
    MachineUserFactory,
    UserFactory,
)
from tests.groups_util import group_has_member

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

    def test_get_groups__returns_groups_ordered_by_display_name_and_external_id(
        self,
        client,
    ):
        second = GroupFactory(
            external_id="engineering-b",
            display_name="Engineering",
        )
        first = GroupFactory(
            external_id="engineering-a",
            display_name="Engineering",
        )
        third = GroupFactory(
            external_id="finance",
            display_name="Finance",
        )
        response = client.get(ENDPOINT)

        assert response.status_code == 200
        assert response.json() == {
            "groups": [
                {
                    "id": str(first.id),
                    "external_id": "engineering-a",
                    "display_name": "Engineering",
                },
                {
                    "id": str(second.id),
                    "external_id": "engineering-b",
                    "display_name": "Engineering",
                },
                {
                    "id": str(third.id),
                    "external_id": "finance",
                    "display_name": "Finance",
                },
            ]
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

        assert group_has_member(session, group.id, first.id)
        assert group_has_member(session, group.id, second.id)

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

        assert not group_has_member(session, group.id, removed.id)
        assert group_has_member(session, group.id, retained.id)

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
        assert group_has_member(session, group.id, member.id)

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
        assert group_has_member(session, group.id, existing.id)

    def test_replace_group_members_requires_permission(self, client):
        group = GroupFactory()
        user = UserFactory()

        response = client.put(
            f"{ENDPOINT}/{group.id}/members",
            json={"member_identity_ids": [str(user.id)]},
        )

        assert response.status_code == 403

    def test_get_group_members__returns_members(self, client):
        group = GroupFactory()
        user = UserFactory()
        machine_user = MachineUserFactory()

        GroupMembershipFactory(group=group, member=user)
        GroupMembershipFactory(group=group, member=machine_user)

        response = client.get(f"{ENDPOINT}/{group.id}/members")

        assert response.status_code == 200
        assert response.json() == {
            "members": sorted(
                [
                    {
                        "group_id": str(group.id),
                        "member_identity_id": str(user.id),
                        "member": {
                            "id": str(user.id),
                            "type": "user",
                            "external_id": user.external_id,
                        },
                    },
                    {
                        "group_id": str(group.id),
                        "member_identity_id": str(machine_user.id),
                        "member": {
                            "id": str(machine_user.id),
                            "type": "machine_user",
                            "external_id": machine_user.external_id,
                        },
                    },
                ],
                key=lambda membership: membership["member_identity_id"],
            )
        }

    def test_get_group_members__excludes_members_of_other_groups(self, client):
        group = GroupFactory()
        other_group = GroupFactory()
        member = UserFactory()
        other_member = UserFactory()

        GroupMembershipFactory(group=group, member=member)
        GroupMembershipFactory(group=other_group, member=other_member)

        response = client.get(f"{ENDPOINT}/{group.id}/members")

        assert response.status_code == 200
        assert response.json() == {
            "members": [
                {
                    "group_id": str(group.id),
                    "member_identity_id": str(member.id),
                    "member": {
                        "id": str(member.id),
                        "type": "user",
                        "external_id": member.external_id,
                    },
                }
            ]
        }

    def test_get_group_members__empty_group_returns_empty_list(self, client):
        group = GroupFactory()

        response = client.get(f"{ENDPOINT}/{group.id}/members")

        assert response.status_code == 200
        assert response.json() == {"members": []}

    def test_get_group_members__unknown_group_returns_not_found(self, client):
        response = client.get(f"{ENDPOINT}/{uuid4()}/members")

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_add_group_members_rejects_more_than_max_members(self, client):
        group = GroupFactory()

        response = client.post(
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(uuid4())
                    for _ in range(settings.MAX_ITEMS_PER_BATCH_REQUEST + 1)
                ]
            },
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_remove_group_members_rejects_more_than_max_members(self, client):
        group = GroupFactory()

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(uuid4())
                    for _ in range(settings.MAX_ITEMS_PER_BATCH_REQUEST + 1)
                ]
            },
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_replace_group_members_rejects_more_than_max_members(self, client):
        group = GroupFactory()

        response = client.request(
            "PUT",
            f"{ENDPOINT}/{group.id}/members",
            json={
                "member_identity_ids": [
                    str(uuid4())
                    for _ in range(settings.MAX_ITEMS_PER_BATCH_REQUEST + 1)
                ]
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_replace_group_members__waits_for_same_group(self):
        group_id = uuid4()
        first_request = _serialize_group_members_replacement(group_id)
        second_request = _serialize_group_members_replacement(group_id)
        second_request_entered = None

        try:
            await anext(first_request)

            second_request_entered = asyncio.create_task(anext(second_request))
            await asyncio.sleep(0)

            assert not second_request_entered.done()

            await first_request.aclose()
            await asyncio.wait_for(second_request_entered, timeout=1)

            assert second_request_entered.done()
        finally:
            await first_request.aclose()
            if second_request_entered is not None and not second_request_entered.done():
                second_request_entered.cancel()
            await second_request.aclose()
