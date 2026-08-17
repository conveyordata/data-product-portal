import pytest

from tests.factories import (
    AccessModeFactory,
    InputPortRequestFactory,
    TechnicalAssetFactory,
)

ENDPOINT = "/api/v2/configuration/access_modes"


@pytest.fixture
def access_mode_payload():
    return {
        "name": "Test Access Mode",
        "description": "Test Description",
        "technical_asset_types": ["RedshiftTechnicalAssetConfiguration"],
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
            "RedshiftTechnicalAssetConfiguration",
            "S3TechnicalAssetConfiguration",
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
                    "S3TechnicalAssetConfiguration",
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
                "RedshiftTechnicalAssetConfiguration",
                "S3TechnicalAssetConfiguration",
            ]
        )
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["S3TechnicalAssetConfiguration"],
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
                "RedshiftTechnicalAssetConfiguration",
                "S3TechnicalAssetConfiguration",
            ]
        )
        TechnicalAssetFactory(
            access_modes=[access_mode],
            configuration__configuration_type="RedshiftTechnicalAssetConfiguration",
        )
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["S3TechnicalAssetConfiguration"],
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
                "RedshiftTechnicalAssetConfiguration",
                "S3TechnicalAssetConfiguration",
            ]
        )
        InputPortRequestFactory(
            access_mode=access_mode,
        )
        response = self.update_access_mode(
            client,
            {
                "description": access_mode.description,
                "technical_asset_types": ["S3TechnicalAssetConfiguration"],
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
