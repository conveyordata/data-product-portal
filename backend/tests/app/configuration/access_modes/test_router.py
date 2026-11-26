import pytest

from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.model import DataProductVisibility
from app.settings import settings
from tests.factories import (
    AccessModeFactory,
    DataProductFactory,
    DefaultAccessModeFactory,
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
    @pytest.mark.parametrize(
        "field", ["technical_asset_types", "default_for_technical_asset_types"]
    )
    def test_create_access_mode__duplicate_technical_asset_types(
        self, access_mode_payload, client, field
    ):
        access_mode_payload[field] = ["FakeLinkPlugin", "FakeLinkPlugin"]
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 422, response.text

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
    def test_update_access_mode__remove_technical_asset_type_used_by_input_port_request(
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
        assert response.status_code == 200, response.text

    def test_get_access_modes(self, client):
        AccessModeFactory()
        response = self.get_access_modes(client)
        assert response.status_code == 200, response.text
        assert len(response.json()["access_modes"]) == 1

    def test_get_access_modes__in_use_by_technical_asset(self, client):
        access_mode = AccessModeFactory(
            technical_asset_types=["FakeLinkPlugin", "FakeTechnicalAssetConfiguration"]
        )
        _hidden_technical_asset(access_mode)

        response = self.get_access_modes(client)

        assert response.status_code == 200, response.text
        assert response.json()["access_modes"][0]["in_use_technical_asset_types"] == [
            "FakeTechnicalAssetConfiguration"
        ]

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

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode__becomes_default_for_type_without_default(
        self, access_mode_payload, client
    ):
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 200, response.text

        assert self.defaults_by_name(client) == {
            access_mode_payload["name"]: ["FakeLinkPlugin"]
        }

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode__keeps_existing_default(
        self, access_mode_payload, client
    ):
        default = _default_access_mode()
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 200, response.text

        assert self.defaults_by_name(client) == {
            default.name: ["FakeLinkPlugin"],
            access_mode_payload["name"]: [],
        }

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode__replaces_default(self, access_mode_payload, client):
        default = _default_access_mode()
        access_mode_payload["default_for_technical_asset_types"] = ["FakeLinkPlugin"]
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 200, response.text

        assert self.defaults_by_name(client) == {
            default.name: [],
            access_mode_payload["name"]: ["FakeLinkPlugin"],
        }

    @pytest.mark.usefixtures("admin")
    def test_create_access_mode__default_for_type_it_does_not_apply_to(
        self, access_mode_payload, client
    ):
        access_mode_payload["default_for_technical_asset_types"] = [
            "FakeTechnicalAssetConfiguration"
        ]
        response = self.create_access_mode(client, access_mode_payload)
        assert response.status_code == 400, response.text

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__replaces_default(self, client):
        default = _default_access_mode()
        access_mode = AccessModeFactory()
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": access_mode.technical_asset_types,
                "default_for_technical_asset_types": ["FakeLinkPlugin"],
            },
            access_mode.id,
        )
        assert response.status_code == 200, response.text

        assert self.defaults_by_name(client) == {
            default.name: [],
            access_mode.name: ["FakeLinkPlugin"],
        }

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__keeps_default_when_omitted(self, client):
        default = _default_access_mode()
        response = self.update_access_mode(
            client,
            {
                "description": "Updated Description",
                "technical_asset_types": default.technical_asset_types,
            },
            default.id,
        )
        assert response.status_code == 200, response.text

        assert self.defaults_by_name(client) == {default.name: ["FakeLinkPlugin"]}

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__remove_type_of_default_with_other_access_modes(
        self, client
    ):
        default = _default_access_mode(
            technical_asset_types=[
                "FakeLinkPlugin",
                "FakeTechnicalAssetConfiguration",
            ]
        )
        AccessModeFactory()
        response = self.update_access_mode(
            client,
            {
                "description": default.description,
                "technical_asset_types": ["FakeTechnicalAssetConfiguration"],
            },
            default.id,
        )
        assert response.status_code == 400, response.text
        assert "default access mode" in response.json()["detail"]

    @pytest.mark.usefixtures("admin")
    def test_update_access_mode__remove_type_of_default_without_other_access_modes(
        self, client
    ):
        default = _default_access_mode(
            technical_asset_types=[
                "FakeLinkPlugin",
                "FakeTechnicalAssetConfiguration",
            ]
        )
        response = self.update_access_mode(
            client,
            {
                "description": default.description,
                "technical_asset_types": ["FakeTechnicalAssetConfiguration"],
            },
            default.id,
        )
        assert response.status_code == 200, response.text

        assert self.defaults_by_name(client) == {
            default.name: ["FakeTechnicalAssetConfiguration"]
        }

    @pytest.mark.usefixtures("admin")
    def test_delete_access_mode__default_with_other_access_modes(self, client):
        default = _default_access_mode()
        AccessModeFactory()
        response = self.delete_access_mode(client, default.id)
        assert response.status_code == 400, response.text
        assert "default access mode" in response.json()["detail"]

    @pytest.mark.usefixtures("admin")
    def test_delete_access_mode__default_without_other_access_modes(self, client):
        default = _default_access_mode()
        response = self.delete_access_mode(client, default.id)
        assert response.status_code == 200, response.text
        assert self.defaults_by_name(client) == {}

    def defaults_by_name(self, client):
        response = self.get_access_modes(client)
        assert response.status_code == 200, response.text
        return {
            access_mode["name"]: access_mode["default_for_technical_asset_types"]
            for access_mode in response.json()["access_modes"]
        }

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


def _default_access_mode(**kwargs):
    access_mode = AccessModeFactory(**kwargs)
    DefaultAccessModeFactory(access_mode=access_mode)
    return access_mode


def _hidden_technical_asset(access_mode):
    return TechnicalAssetFactory(
        access_modes=[access_mode],
        owner=DataProductFactory(visibility=DataProductVisibility.HIDDEN),
    )
