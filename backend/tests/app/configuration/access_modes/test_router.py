import pytest

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.model import DataProductVisibility
from app.settings import settings
from tests.factories import (
    AccessModeFactory,
    DataProductFactory,
    GlobalRoleAssignmentFactory,
    InputPortRequestFactory,
    RoleFactory,
    TechnicalAssetFactory,
    UserFactory,
)

ENDPOINT = "/api/v2/configuration/access_modes"


@pytest.fixture
def configuration_manager():
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    role = RoleFactory(
        scope=Scope.GLOBAL, permissions=[Action.GLOBAL__UPDATE_CONFIGURATION]
    )
    GlobalRoleAssignmentFactory(identity_id=user.id, role_id=role.id)
    return user


@pytest.fixture
def access_mode_payload():
    return {
        "name": "Test Access Mode",
        "description": "Test Description",
        "technical_asset_types": ["FakeLinkPlugin"],
    }


class TestAccessModesRouter:
    @pytest.mark.usefixtures("admin")
    def test_create_access_mode(self, access_mode_payload, client):
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode_unique(self, access_mode_payload, client):
        AccessModeFactory(name=access_mode_payload["name"])
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 400, response.json()

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode_multiple_technical_asset_types(
        self, access_mode_payload, client
    ):
        access_mode_payload["technical_asset_types"] = [
            "FakeLinkPlugin",
            "FakeTechnicalAssetConfiguration",
        ]
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 200
        assert "id" in response.json()

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode_unsupported_plugin(self, access_mode_payload, client):
        access_mode_payload["technical_asset_types"] = ["NonExistentPlugin"]
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode(self, client):
        access_mode = AccessModeFactory()
        response = self.update_access_mode(
            client,
            {
                "description": "Updated Description",
                "technical_asset_types": [
                    "FakeTechnicalAssetConfiguration",
                    *access_mode.technical_asset_types,
                ],
            },
            access_mode.id,
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(access_mode.id)

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__remove_technical_asset_type(self, client):
        access_mode = AccessModeFactory(
            technical_asset_types=[
                "FakeLinkPlugin",
                "FakeTechnicalAssetConfiguration",
            ]
        )
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["FakeTechnicalAssetConfiguration"],
            },
            access_mode.id,
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(access_mode.id)

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__remove_technical_asset_type_in_use_by_technical_asset(
        self, client
    ):
        access_mode = AccessModeFactory(
            technical_asset_types=[
                "FakeLinkPlugin",
                "FakeTechnicalAssetConfiguration",
            ]
        )
        TechnicalAssetFactory(access_modes=[access_mode])
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["FakeLinkPlugin"],
            },
            access_mode.id,
        )
        assert response.status_code == 400

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__remove_technical_asset_type_in_use_by_input_port_request(
        self, client
    ):
        access_mode = AccessModeFactory(
            technical_asset_types=[
                "FakeLinkPlugin",
                "FakeTechnicalAssetConfiguration",
            ]
        )
        InputPortRequestFactory(
            access_mode=access_mode,
        )
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["FakeTechnicalAssetConfiguration"],
            },
            access_mode.id,
        )
        assert response.status_code == 400

    def test_get_access_modes(self, client):
        AccessModeFactory()
        response = self.get_access_modes(client)
        assert response.status_code == 200, response.text
        assert len(response.json()["access_modes"]) == 1

    @pytest.mark.usefixtures("admin")
    def test_delete_access_mode__success(self, client):
        access_mode = AccessModeFactory()
        response = self.delete_access_mode(client, access_mode.id)
        assert response.status_code == 200

    @pytest.mark.usefixtures("admin")
    def test_delete_access_mode__linked_to_input_port_request(self, client):
        access_mode = AccessModeFactory()
        InputPortRequestFactory(access_mode=access_mode)
        response = self.delete_access_mode(client, access_mode.id)
        assert response.status_code == 400, response.json()

    @pytest.mark.usefixtures("admin")
    def test_delete_access_mode__linked_to_technical_asset(self, client):
        access_mode = AccessModeFactory()
        TechnicalAssetFactory(access_modes=[access_mode])
        response = self.delete_access_mode(client, access_mode.id)
        assert response.status_code == 400, response.json()

    @pytest.mark.usefixtures("configuration_manager")
    def test_update_access_mode__remove_technical_asset_type_in_use_by_hidden_technical_asset(
        self, client
    ):
        access_mode = AccessModeFactory(
            technical_asset_types=[
                "FakeLinkPlugin",
                "FakeTechnicalAssetConfiguration",
            ]
        )
        _hidden_technical_asset(access_mode)
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["FakeLinkPlugin"],
            },
            access_mode.id,
        )
        assert response.status_code == 400, response.json()

    @pytest.mark.usefixtures("configuration_manager")
    def test_delete_access_mode__linked_to_hidden_technical_asset(self, client):
        access_mode = AccessModeFactory()
        _hidden_technical_asset(access_mode)
        response = self.delete_access_mode(client, access_mode.id)
        assert response.status_code == 400, response.json()
        assert "in use" in response.json()["detail"]

    @staticmethod
    def create_access_mode(client, payload):
        return client.post(ENDPOINT, json=payload)

    @staticmethod
    def update_access_mode(client, payload, access_mode_id):
        return client.put(f"{ENDPOINT}/{access_mode_id}", json=payload)

    @staticmethod
    def get_access_modes(client):
        return client.get(ENDPOINT)

    @staticmethod
    def delete_access_mode(client, access_mode_id):
        return client.delete(f"{ENDPOINT}/{access_mode_id}")


def _hidden_technical_asset(access_mode):
    return TechnicalAssetFactory(
        access_modes=[access_mode],
        owner=DataProductFactory(visibility=DataProductVisibility.HIDDEN),
    )
