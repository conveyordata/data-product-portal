from typing import Any
from uuid import uuid4

import pytest

from tests.factories import GroupFactory, MachineUserFactory
from app.machine_users.model import MachineUser
from app.settings import settings
from tests.factories import UserFactory

ENDPOINT = "/api/v2/machine-users"


@pytest.fixture
def machine_user_payload() -> dict[str, str]:
    return {
        "external_id": "deployment-agent",
        "display_name": "Deployment Agent",
    }


class TestMachineUsersRouter:
    def test_get_machine_user__returns_machine_user(self, client):
        machine_user = MachineUserFactory(
            external_id="deployment-agent",
            display_name="Deployment Agent",
        )

        response = client.get(f"{ENDPOINT}/{machine_user.id}")

        assert response.status_code == 200
        assert response.json() == {
            "id": str(machine_user.id),
            "external_id": "deployment-agent",
            "display_name": "Deployment Agent",
        }

    def test_get_machine_users__returns_machine_users_ordered_by_display_name_and_external_id(
        self,
        client,
    ):
        second = MachineUserFactory(
            external_id="deployment-agent-b",
            display_name="Deployment Agent",
        )
        first = MachineUserFactory(
            external_id="deployment-agent-a",
            display_name="Deployment Agent",
        )
        third = MachineUserFactory(
            external_id="monitoring-agent",
            display_name="Monitoring Agent",
        )
        response = client.get(ENDPOINT)

        assert response.status_code == 200
        assert response.json() == {
            "machine_users": [
                {
                    "id": str(first.id),
                    "external_id": "deployment-agent-a",
                    "display_name": "Deployment Agent",
                },
                {
                    "id": str(second.id),
                    "external_id": "deployment-agent-b",
                    "display_name": "Deployment Agent",
                },
                {
                    "id": str(third.id),
                    "external_id": "monitoring-agent",
                    "display_name": "Monitoring Agent",
                },
            ]
        }

    def test_get_machine_user__unknown_id_returns_not_found(self, client):
        response = client.get(f"{ENDPOINT}/{uuid4()}")

        assert response.status_code == 404

    def test_get_machine_user__group_id_returns_not_found(self, client):
        group = GroupFactory()

        response = client.get(f"{ENDPOINT}/{group.id}")

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_create_machine_user__creates_machine_user(
        self,
        client,
        machine_user_payload,
    ):
        response = client.post(
            ENDPOINT,
            json=machine_user_payload,
        )

        assert response.status_code == 200
        machine_user_id = response.json()["id"]

        get_response = client.get(
            f"{ENDPOINT}/{machine_user_id}",
        )
        assert get_response.status_code == 200
        assert get_response.json() == {
            "id": machine_user_id,
            **machine_user_payload,
        }

    def test_create_machine_user__without_permission_returns_forbidden(
        self,
        client,
        machine_user_payload,
    ):
        response = client.post(
            ENDPOINT,
            json=machine_user_payload,
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    @pytest.mark.parametrize(
        "payload",
        [
            {"display_name": "Deployment Agent"},
            {"external_id": "deployment-agent"},
            {},
        ],
    )
    def test_create_machine_user__incomplete_payload_is_rejected(
        self,
        client,
        payload: dict[str, Any],
    ):
        response = client.post(ENDPOINT, json=payload)

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_create_machine_user__duplicate_external_id_is_rejected(
        self,
        client,
        machine_user_payload,
    ):
        MachineUserFactory(
            external_id=machine_user_payload["external_id"],
        )

        response = client.post(
            ENDPOINT,
            json=machine_user_payload,
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "A machine user with this external ID already exists."
        )

    @pytest.mark.usefixtures("admin")
    def test_update_machine_user__updates_mutable_fields(self, client):
        machine_user = MachineUserFactory(
            external_id="deployment-agent",
            display_name="Old name",
        )

        response = client.put(
            f"{ENDPOINT}/{machine_user.id}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 200
        assert response.json() == {"id": str(machine_user.id)}

        get_response = client.get(
            f"{ENDPOINT}/{machine_user.id}",
        )
        assert get_response.json() == {
            "id": str(machine_user.id),
            "external_id": "deployment-agent",
            "display_name": "New name",
        }

    def test_update_machine_user__without_permission_returns_forbidden(
        self,
        client,
    ):
        machine_user = MachineUserFactory()

        response = client.put(
            f"{ENDPOINT}/{machine_user.id}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    def test_update_machine_user__missing_display_name_is_rejected(
        self,
        client,
    ):
        machine_user = MachineUserFactory()

        response = client.put(
            f"{ENDPOINT}/{machine_user.id}",
            json={},
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_update_machine_user__external_id_is_rejected(
        self,
        client,
    ):
        machine_user = MachineUserFactory(
            external_id="original-external-id",
            display_name="Old name",
        )

        response = client.put(
            f"{ENDPOINT}/{machine_user.id}",
            json={
                "external_id": "modified-external-id",
                "display_name": "New name",
            },
        )

        assert response.status_code == 422

        get_response = client.get(
            f"{ENDPOINT}/{machine_user.id}",
        )
        assert get_response.json() == {
            "id": str(machine_user.id),
            "external_id": "original-external-id",
            "display_name": "Old name",
        }

    @pytest.mark.usefixtures("admin")
    def test_update_machine_user__unknown_id_returns_not_found(
        self,
        client,
    ):
        response = client.put(
            f"{ENDPOINT}/{uuid4()}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_update_machine_user__group_id_returns_not_found(
        self,
        client,
    ):
        group = GroupFactory()

        response = client.put(
            f"{ENDPOINT}/{group.id}",
            json={"display_name": "New name"},
        )

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_delete_machine_user__deletes_machine_user(self, client):
        machine_user = MachineUserFactory()

        response = client.delete(
            f"{ENDPOINT}/{machine_user.id}",
        )

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get(
            f"{ENDPOINT}/{machine_user.id}",
        )
        assert get_response.status_code == 404

    def test_delete_machine_user__without_permission_returns_forbidden(
        self,
        client,
    ):
        machine_user = MachineUserFactory()

        response = client.delete(
            f"{ENDPOINT}/{machine_user.id}",
        )

        assert response.status_code == 403
        assert (
            client.get(
                f"{ENDPOINT}/{machine_user.id}",
            ).status_code
            == 200
        )

    @pytest.mark.usefixtures("admin")
    def test_delete_machine_user__unknown_id_returns_not_found(
        self,
        client,
    ):
        response = client.delete(f"{ENDPOINT}/{uuid4()}")

        assert response.status_code == 404

    @pytest.mark.usefixtures("admin")
    def test_create_machine_users_batch__creates_valid_items_and_returns_errors(
        self, client, session
    ):
        invalid_item = {
            "external_id": "",
            "display_name": "",
        }

        response = client.post(
            f"{ENDPOINT}/batch",
            json={
                "items": [
                    {
                        "external_id": "deployment-agent",
                        "display_name": "Deployment Agent",
                    },
                    invalid_item,
                ]
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["ids"]) == 1
        assert len(body["errors"]) == 1
        assert body["errors"][0]["item"] == invalid_item
        assert len(body["errors"][0]["errors"]) == 2

        created = session.get(MachineUser, body["ids"][0])
        assert created is not None
        assert created.external_id == "deployment-agent"

    def test_create_machine_users_batch__without_permission_returns_forbidden(
        self, client
    ):
        response = client.post(
            f"{ENDPOINT}/batch",
            json={
                "items": [
                    {
                        "external_id": "deployment-agent",
                        "display_name": "Deployment Agent",
                    }
                ]
            },
        )

        assert response.status_code == 403

    @pytest.mark.usefixtures("admin")
    @pytest.mark.parametrize(
        "items",
        [
            [],
            [{}] * (settings.MAX_ITEMS_PER_BATCH_REQUEST + 1),
        ],
    )
    def test_create_machine_users_batch__rejects_invalid_list_size(
        self, client, items
    ):
        response = client.post(
            f"{ENDPOINT}/batch",
            json={"items": items},
        )

        assert response.status_code == 422

    @pytest.mark.usefixtures("admin")
    def test_delete_machine_users_batch__deletes_machine_users(
        self, client, session
    ):
        first = MachineUserFactory()
        second = MachineUserFactory()

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/batch",
            json={"ids": [str(first.id), str(second.id)]},
        )

        assert response.status_code == 204
        assert response.content == b""
        assert session.get(MachineUser, first.id) is None
        assert session.get(MachineUser, second.id) is None

    @pytest.mark.usefixtures("admin")
    def test_delete_machine_users_batch__ignores_unknown_and_wrong_type_ids(
        self, client, session
    ):
        machine_user = MachineUserFactory()
        user = UserFactory()

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/batch",
            json={
                "ids": [
                    str(machine_user.id),
                    str(user.id),
                    str(uuid4()),
                ]
            },
        )

        assert response.status_code == 204
        assert session.get(MachineUser, machine_user.id) is None
        assert user in session

    def test_delete_machine_users_batch__without_permission_returns_forbidden(
        self, client, session
    ):
        machine_user = MachineUserFactory()

        response = client.request(
            "DELETE",
            f"{ENDPOINT}/batch",
            json={"ids": [str(machine_user.id)]},
        )

        assert response.status_code == 403
        assert session.get(MachineUser, machine_user.id) is not None

    @pytest.mark.usefixtures("admin")
    @pytest.mark.parametrize(
        "ids",
        [
            [],
            ["not-a-uuid"],
            ["00000000-0000-0000-0000-000000000001"] * 2,
            [
                str(uuid4())
                for _ in range(settings.MAX_ITEMS_PER_BATCH_REQUEST + 1)
            ],
        ],
    )
    def test_delete_machine_users_batch__rejects_invalid_request(
        self, client, ids
    ):
        response = client.request(
            "DELETE",
            f"{ENDPOINT}/batch",
            json={"ids": ids},
        )

        assert response.status_code == 422
