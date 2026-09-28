from typing import Any
from uuid import uuid4

import pytest

from tests.factories import (
    GroupFactory,
    MachineUserFactory,
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
        assert response.json() == {
            "detail": "A group with this external ID already exists."
        }

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

