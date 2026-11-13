import uuid
from copy import deepcopy
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from portal_plugins.azure_keyvault.model import (
    AzureKeyVaultTechnicalAssetConfiguration as KeyVaultConfigurationModel,
)
from portal_plugins.azure_keyvault.schema import (
    AzureKeyVaultTechnicalAssetConfiguration,
)
from sqlalchemy import func, select

from app.authorization.roles.model import Role
from app.authorization.roles.schema import Scope
from app.core.authz import Action
from app.data_products.model import DataProduct, DataProductEnvironment
from app.database.database import SKIP_DATA_PRODUCT_VISIBILITY_FILTER
from app.settings import settings
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from tests.app.data_products.output_port_technical_assets_link.test_router import (
    TECHNICAL_ASSETS_OUTPUT_PORTS_ENDPOINT,
)
from tests.factories import (
    AccessModeFactory,
    DataProductFactory,
    DataProductRoleAssignmentFactory,
    DatasetRoleAssignmentFactory,
    DomainFactory,
    EnvironmentFactory,
    EnvPlatformServiceConfigFactory,
    OutputPortFactory,
    PlatformServiceFactory,
    RoleFactory,
    TagFactory,
    TechnicalAssetFactory,
    UserFactory,
)
from tests.webhook_util import assert_event_in_queue

ENDPOINT = "/api/v2/data_products/{}/technical_assets"


@pytest.fixture
def technical_asset_payload():
    user = UserFactory(external_id=settings.DEFAULT_USERNAME)
    data_product = DataProductFactory()
    service = PlatformServiceFactory()
    tag = TagFactory()

    return {
        "name": "Data Output Name",
        "description": "Updated Data Output Description",
        "namespace": "namespace-updated",
        "technical_mapping": "custom",
        "configuration": {
            "path": "test",
            "name": "FakeTechnicalAssetConfiguration",
        },
        "owner_id": str(data_product.id),
        "platform_id": str(service.platform.id),
        "service_id": str(service.id),
        "status": "pending",
        "tag_ids": [str(tag.id)],
        "user_id": str(user.id),
    }


@pytest.fixture
def data_product_role_assignment(technical_asset_payload) -> Role:
    role = RoleFactory(
        scope=Scope.DATA_PRODUCT,
        permissions=[Action.DATA_PRODUCT__CREATE_TECHNICAL_ASSET],
    )
    DataProductRoleAssignmentFactory(
        identity_id=technical_asset_payload["user_id"],
        role_id=role.id,
        data_product_id=technical_asset_payload["owner_id"],
    )
    return role


class TestKeyVaultTechnicalAssets:
    @pytest.fixture
    def keyvault_payload(self, monkeypatch, admin):
        plugin = AzureKeyVaultTechnicalAssetConfiguration
        monkeypatch.setattr(
            settings, "ENABLED_PLUGINS", [*settings.ENABLED_PLUGINS, plugin.name]
        )
        metadata = plugin.get_platform_metadata()
        service = PlatformServiceFactory(
            result_string_template=metadata.result_string_template,
            technical_info_template=metadata.technical_info_template,
        )
        environment = EnvironmentFactory(name="Production", acronym="prd")
        data_product = DataProductFactory(
            environments=[DataProductEnvironment(environment=environment)]
        )
        EnvPlatformServiceConfigFactory(
            platform=service.platform,
            service=service,
            environment=environment,
            config="[]",
        )
        return {
            "name": "copilot-usage",
            "namespace": "namespace-longer-than-thirteen",
            "description": "Secrets",
            "technical_mapping": "default",
            "configuration": {"name": plugin.name, "vault_name": "client-override"},
            "platform_id": str(service.platform.id),
            "service_id": str(service.id),
            "owner_id": str(data_product.id),
            "tag_ids": [],
        }

    def test_create_and_rename__preserves_vault_identity(
        self, client, keyvault_payload
    ):
        TechnicalAssetFactory(name=keyvault_payload["name"])
        endpoint = ENDPOINT.format(keyvault_payload["owner_id"])
        created = client.post(endpoint, json=keyvault_payload)
        assert created.status_code == 200, created.text
        asset_endpoint = f"{endpoint}/{created.json()['id']}"

        before = client.get(asset_endpoint)
        assert before.status_code == 200, before.text
        assert before.json()["configuration"]["vault_name"] == "kv-adp-copilot-usage"
        assert before.json()["namespace"] == keyvault_payload["namespace"]
        assert before.json()["result_string"] == "kv-adp-copilot-usage"
        assert before.json()["technical_info"][0]["info"] == (
            "https://kv-adp-copilot-usage-prd.vault.azure.net/"
        )

        renamed = client.put(
            asset_endpoint,
            json={
                "name": "Copilot usage secrets!",
                "description": "Updated description",
                "tag_ids": [],
            },
        )
        assert renamed.status_code == 200, renamed.text
        after = client.get(asset_endpoint)
        assert after.status_code == 200, after.text
        assert after.json()["name"] == "Copilot usage secrets!"
        for field in ("configuration", "result_string", "technical_info", "namespace"):
            assert after.json()[field] == before.json()[field]

        other_product = DataProductFactory()
        duplicate = client.post(
            ENDPOINT.format(other_product.id),
            json={**keyvault_payload, "namespace": "another-namespace"},
        )
        assert duplicate.status_code == 400, duplicate.text
        assert duplicate.json()["detail"] == (
            "Key Vault kv-adp-copilot-usage already exists"
        )

    @pytest.mark.parametrize("name", ["a" * 14, "Invalid name"])
    def test_create__rejects_invalid_vault_name(
        self, client, session, keyvault_payload, name
    ):
        response = client.post(
            ENDPOINT.format(keyvault_payload["owner_id"]),
            json={**keyvault_payload, "name": name},
        )

        assert response.status_code == 400, response.text
        assert "Key Vault name" in response.json()["detail"]
        assert (
            session.scalar(select(func.count()).select_from(KeyVaultConfigurationModel))
            == 0
        )

    def test_create__rejects_duplicate_when_precheck_misses_conflict(
        self, client, session, keyvault_payload, monkeypatch
    ):
        created = client.post(
            ENDPOINT.format(keyvault_payload["owner_id"]), json=keyvault_payload
        )
        assert created.status_code == 200, created.text
        other_product = DataProductFactory()
        validate = AzureKeyVaultTechnicalAssetConfiguration.validate_configuration

        def validate_without_existing_vault(configuration, context, db):
            with patch.object(db, "scalar", return_value=False):
                validate(configuration, context, db)

        monkeypatch.setattr(
            AzureKeyVaultTechnicalAssetConfiguration,
            "validate_configuration",
            validate_without_existing_vault,
        )
        duplicate = client.post(
            ENDPOINT.format(other_product.id),
            json={**keyvault_payload, "namespace": "another-namespace"},
        )

        assert duplicate.status_code == 400, duplicate.text
        assert "uq_azure_keyvault_vault_name" in duplicate.json()["detail"]
        assert (
            session.scalar(select(func.count()).select_from(KeyVaultConfigurationModel))
            == 1
        )
        assert (
            session.scalar(select(func.count()).select_from(TechnicalAssetConfiguration))
            == 1
        )
        assert client.get(
            f"{ENDPOINT.format(keyvault_payload['owner_id'])}/{created.json()['id']}"
        ).status_code == 200

    def test_delete__removes_configuration_and_allows_name_reuse(
        self, client, session, keyvault_payload
    ):
        endpoint = ENDPOINT.format(keyvault_payload["owner_id"])
        created = client.post(endpoint, json=keyvault_payload)
        assert created.status_code == 200, created.text
        configuration_id = session.scalar(select(KeyVaultConfigurationModel.id))
        assert configuration_id is not None

        deleted = client.delete(f"{endpoint}/{created.json()['id']}")
        assert deleted.status_code == 200, deleted.text
        assert session.get(KeyVaultConfigurationModel, configuration_id) is None
        assert session.get(TechnicalAssetConfiguration, configuration_id) is None

        recreated = client.post(endpoint, json=keyvault_payload)
        assert recreated.status_code == 200, recreated.text


class TestTechnicalAssetsRouter:
    invalid_id = "00000000-0000-0000-0000-000000000000"

    def test_create_technical_asset(
        self, technical_asset_payload, data_product_role_assignment, client: TestClient
    ):
        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 200, created_technical_asset.text
        assert "id" in created_technical_asset.json()

    def test_create_technical_asset__with_platform_and_service_omitted(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        technical_asset_payload.pop("platform_id")
        technical_asset_payload.pop("service_id")

        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 200, created_technical_asset.text

        technical_asset = self.get_technical_asset(
            client,
            technical_asset_payload["owner_id"],
            created_technical_asset.json()["id"],
        )
        assert technical_asset.status_code == 200, technical_asset.text
        body = technical_asset.json()
        assert body["platform_id"] is None
        assert body["service_id"] is None
        assert body["result_string"] == ""
        assert body["technical_info"] == []

    def test_create_technical_asset__rejects_only_one_of_platform_id_or_service_id(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        technical_asset_payload["service_id"] = None

        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )

        assert created_technical_asset.status_code == 422, created_technical_asset.text

    def test_create_technical_asset__with_access_modes(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        access_mode = AccessModeFactory(
            technical_asset_types=[technical_asset_payload["configuration"]["name"]]
        )
        technical_asset_payload["access_mode_ids"] = [
            str(access_mode.id),
        ]

        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 200

        technical_asset = self.get_technical_asset(
            client,
            technical_asset_payload["owner_id"],
            created_technical_asset.json()["id"],
        )
        assert technical_asset.status_code == 200, technical_asset.text
        assert len(technical_asset.json()["access_modes"]) == 1
        assert technical_asset.json()["access_modes"][0]["name"] == access_mode.name

    def test_create_technical_asset__incorrect_access_modes(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        access_mode = AccessModeFactory()
        technical_asset_payload["access_mode_ids"] = [
            str(access_mode.id),
        ]

        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 400

    def test_create_technical_asset__access_mode_doest_not_exist(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        technical_asset_payload["access_mode_ids"] = [
            str(uuid.uuid4()),
        ]
        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 400

    def test_create_technical_asset_generates_webhook_v2_event(
        self,
        technical_asset_payload,
        data_product_role_assignment,
        client: TestClient,
        capture_events,
    ):
        self.test_create_technical_asset(
            technical_asset_payload, data_product_role_assignment, client
        )
        assert_event_in_queue("technical_asset.event", capture_events)

    def test_create_technical_asset_product_aligned(
        self, technical_asset_payload, data_product_role_assignment, client: TestClient
    ):
        payload = deepcopy(technical_asset_payload)
        payload["technical_mapping"] = "default"

        created_technical_asset = self.create_technical_asset(client, payload)
        assert created_technical_asset.status_code == 200
        assert "id" in created_technical_asset.json()

    def test_create_technical_asset_product_aligned_new(
        self, technical_asset_payload, data_product_role_assignment, client: TestClient
    ):
        payload = deepcopy(technical_asset_payload)
        payload["technical_mapping"] = "default"

        created_technical_asset = self.create_technical_asset(client, payload)
        assert created_technical_asset.status_code == 200
        assert "id" in created_technical_asset.json()

    def test_deprecated_source_aligned(
        self, technical_asset_payload, data_product_role_assignment, client: TestClient
    ):
        payload = deepcopy(technical_asset_payload)
        payload.pop("technical_mapping")
        payload["sourceAligned"] = True

        created_technical_asset = self.create_technical_asset(client, payload)
        assert created_technical_asset.status_code == 200
        assert "id" in created_technical_asset.json()
        assert (
            self.get_technical_asset(
                client,
                technical_asset_payload["owner_id"],
                created_technical_asset.json().get("id"),
            ).json()["technical_mapping"]
            == "custom"
        )

    def test_create_technical_asset_not_product_owner(
        self, technical_asset_payload, client: TestClient
    ):
        technical_asset_payload.pop("user_id")
        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 403

    def test_get_technical_assets(self, client):
        technical_asset = TechnicalAssetFactory()
        response = client.get(ENDPOINT.format(technical_asset.owner.id))
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1
        assert data["technical_assets"][0]["id"] == str(technical_asset.id)

    def test_get_technical_asset(self, client: TestClient):
        technical_asset = TechnicalAssetFactory()

        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(technical_asset.id)

    def test_get_technical_asset__environment_info_uses_saved_data_product_list(
        self, client: TestClient
    ):
        dev_env = EnvironmentFactory(name="dev", acronym="dev")
        prd_env = EnvironmentFactory(name="prd", acronym="prd")
        data_product = DataProductFactory(
            id=uuid.uuid4(),
            environments=[
                DataProductEnvironment(environment=dev_env),
                DataProductEnvironment(environment=prd_env),
            ],
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=dev_env,
        )
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=prd_env,
        )

        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200
        environment_ids = {
            info["environment_id"] for info in response.json()["technical_info"]
        }
        assert environment_ids == {str(dev_env.id), str(prd_env.id)}
        assert {
            item["environment_id"] for item in response.json()["environments"]
        } == environment_ids

    def test_get_technical_asset__environment_info_excludes_undeclared_environments(
        self, client: TestClient
    ):
        dev_env = EnvironmentFactory(name="dev", acronym="dev", is_global=True)
        sandbox_env = EnvironmentFactory(
            name="sandbox", acronym="sandbox", is_global=False
        )
        data_product = DataProductFactory(
            environments=[DataProductEnvironment(environment=dev_env)]
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=dev_env,
        )
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=sandbox_env,
        )

        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200
        environment_ids = {
            info["environment_id"] for info in response.json()["technical_info"]
        }
        assert environment_ids == {str(dev_env.id)}

    def test_get_technical_asset__environment_info_uses_data_product_scope(
        self, client: TestClient
    ):
        dev_env = EnvironmentFactory(name="dev", acronym="dev")
        prd_env = EnvironmentFactory(name="prd", acronym="prd")
        domain = DomainFactory()
        data_product = DataProductFactory(
            domain=domain, environments=[DataProductEnvironment(environment=dev_env)]
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=dev_env,
        )
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=prd_env,
        )

        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200
        environment_ids = {
            info["environment_id"] for info in response.json()["technical_info"]
        }
        assert environment_ids == {str(dev_env.id)}

    def test_get_technical_asset__data_product_can_include_non_global_environment(
        self, client: TestClient
    ):
        sandbox_env = EnvironmentFactory(
            name="sandbox", acronym="sandbox", is_global=False
        )
        prd_env = EnvironmentFactory(name="prd", acronym="prd", is_global=True)
        domain = DomainFactory()
        data_product = DataProductFactory(
            domain=domain,
            environments=[DataProductEnvironment(environment=sandbox_env)],
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=sandbox_env,
        )
        EnvPlatformServiceConfigFactory(
            platform=technical_asset.platform,
            service=technical_asset.service,
            environment=prd_env,
        )

        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200
        environment_ids = {
            info["environment_id"] for info in response.json()["technical_info"]
        }
        assert environment_ids == {str(sandbox_env.id)}

    def test_get_technical_asset_by_id_not_found(self, client: TestClient):
        technical_asset = TechnicalAssetFactory()
        response = self.get_technical_asset(
            client, technical_asset.owner.id, uuid.uuid4()
        )
        assert response.status_code == 404

    def test_update_technical_asset(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        tag = TagFactory()
        technical_asset = TechnicalAssetFactory(owner=data_product)
        update_payload = {
            "name": "update",
            "description": "update",
            "tag_ids": [str(tag.id)],
        }
        response = self.update_technical_asset(
            client, update_payload, technical_asset.owner.id, technical_asset.id
        )

        assert response.status_code == 200, response.text
        assert response.json()["id"] == str(technical_asset.id)

    def test_update_data_product_no_member(self, client: TestClient):
        technical_asset = TechnicalAssetFactory()
        response = self.update_technical_asset(
            client,
            {"name": "update", "description": "update"},
            technical_asset.owner.id,
            technical_asset.id,
        )
        assert response.status_code == 403

    def test_remove_technical_asset_no_access(self, client: TestClient):
        technical_asset = TechnicalAssetFactory()
        response = self.delete_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 403

    def test_remove_technical_asset(self, client: TestClient, session):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        configuration_id = technical_asset.configuration_id
        configuration_type = type(technical_asset.configuration)
        response = self.delete_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200
        assert session.get(configuration_type, configuration_id) is None
        assert session.get(TechnicalAssetConfiguration, configuration_id) is None

    def test_remove_technical_asset_with_tags(self, client: TestClient):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product, tags=[TagFactory()])
        response = self.delete_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200

    def test_update_status_not_owner(self, client: TestClient):
        do = TechnicalAssetFactory()
        response = self.update_technical_asset_status(
            client, {"status": "active"}, do.owner.id, do.id
        )
        assert response.status_code == 403

    def test_update_status(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.json()["status"] == "active"
        _ = self.update_technical_asset_status(
            client, {"status": "pending"}, technical_asset.owner.id, technical_asset.id
        )
        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.json()["status"] == "pending"

    def test_update_technical_asset_status(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.json()["status"] == "active"
        _ = self.update_technical_asset_status(
            client, {"status": "pending"}, technical_asset.owner.id, technical_asset.id
        )
        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.json()["status"] == "pending"

    def test_get_graph_data(self, client: TestClient):
        technical_asset = TechnicalAssetFactory()
        response = client.get(
            f"{ENDPOINT.format(technical_asset.owner.id)}/{technical_asset.id}/graph"
        )
        assert response.json()["edges"] == [
            {
                "animated": True,
                "id": f"{str(technical_asset.id)}-{str(technical_asset.owner.id)}",
                "source": str(technical_asset.owner.id),
                "target": str(technical_asset.id),
                "sourceHandle": "right_s",
                "targetHandle": "left_t",
            }
        ]
        for node in response.json()["nodes"]:
            if node["type"] == "technicalAssetNode":
                assert node == {
                    "data": {
                        "icon_key": "FakeTechnicalAssetConfiguration",
                        "id": str(technical_asset.id),
                        "link_to_id": str(technical_asset.owner.id),
                        "name": technical_asset.name,
                        "domain": None,
                        "domain_id": None,
                        "description": None,
                    },
                    "id": str(technical_asset.id),
                    "isMain": True,
                    "type": "technicalAssetNode",
                }
            else:
                assert node == {
                    "data": {
                        "icon_key": "default",
                        "id": str(technical_asset.owner.id),
                        "link_to_id": None,
                        "name": technical_asset.owner.name,
                        "domain": None,
                        "domain_id": None,
                        "description": None,
                    },
                    "id": str(technical_asset.owner.id),
                    "isMain": False,
                    "type": "dataProductNode",
                }

    def test_get_namespace_suggestion_substitution(self, client: TestClient):
        name = "test with spaces"
        response = self.get_namespace_suggestion(client, name)
        body = response.json()

        assert response.status_code == 200
        assert body["resource_name"] == "test-with-spaces"

    def test_get_namespace_length_limits(self, client):
        response = self.get_namespace_length_limits(client)
        assert response.status_code == 200
        assert response.json()["max_length"] > 1

    def test_get_namespace_validation(self, client: TestClient):
        namespace = "valid-namespace"
        data_product = DataProductFactory()
        response = self.get_namespace_validation(
            client, namespace, str(data_product.id)
        )
        body = response.json()

        assert response.status_code == 200
        assert body["validity"] == "VALID"

    def test_create_technical_asset_duplicate_namespace(
        self,
        technical_asset_payload,
        data_product_role_assignment,
        client: TestClient,
        session,
    ):
        data_product = session.get(
            DataProduct,
            str(technical_asset_payload["owner_id"]),
            execution_options={SKIP_DATA_PRODUCT_VISIBILITY_FILTER: True},
        )
        TechnicalAssetFactory(
            namespace=technical_asset_payload["namespace"], owner=data_product
        )
        response = self.create_technical_asset(client, technical_asset_payload)
        assert response.status_code == 400

    def test_create_technical_asset_invalid_characters_namespace(
        self, technical_asset_payload, data_product_role_assignment, client: TestClient
    ):
        create_payload = deepcopy(technical_asset_payload)
        create_payload["namespace"] = "!"

        response = self.create_technical_asset(client, create_payload)
        assert response.status_code == 400

    def test_create_technical_asset_invalid_length_namespace(
        self, technical_asset_payload, data_product_role_assignment, client: TestClient
    ):
        create_payload = deepcopy(technical_asset_payload)
        create_payload["namespace"] = "a" * 256

        response = self.create_technical_asset(client, create_payload)
        assert response.status_code == 400

    def test_history_event_created_on_technical_asset_creation(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 200
        assert "id" in created_technical_asset.json()

        history = self.get_technical_asset_history(
            client,
            technical_asset_payload["owner_id"],
            created_technical_asset.json().get("id"),
        ).json()
        assert len(history["events"]) == 1

    def test_get_technical_asset_history(
        self, technical_asset_payload, data_product_role_assignment, client
    ):
        created_technical_asset = self.create_technical_asset(
            client, technical_asset_payload
        )
        assert created_technical_asset.status_code == 200
        assert "id" in created_technical_asset.json()

        history = self.get_technical_asset_history(
            client,
            technical_asset_payload["owner_id"],
            created_technical_asset.json().get("id"),
        )
        assert history.status_code == 200, history.text
        assert len(history.json()["events"]) == 1

    def test_history_event_created_on_technical_asset_status_update(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        response = self.update_technical_asset_status(
            client, {"status": "pending"}, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200, response.text
        response = self.get_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200, response.text

        history = self.get_technical_asset_history(
            client, technical_asset.owner.id, technical_asset.id
        ).json()
        assert len(history["events"]) == 1

    def test_history_event_created_on_technical_asset_update(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__UPDATE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        tag = TagFactory()
        technical_asset = TechnicalAssetFactory(owner=data_product)
        update_payload = {
            "name": "update",
            "description": "update",
            "tag_ids": [str(tag.id)],
        }
        response = self.update_technical_asset(
            client, update_payload, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200

        history = self.get_technical_asset_history(
            client, technical_asset.owner.id, technical_asset.id
        ).json()
        assert len(history["events"]) == 1

    def test_history_event_created_on_technical_asset_deletion(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        response = self.delete_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200

        # get_data_product_history should return 1
        history = self.get_data_product_history(client, technical_asset.owner.id).json()
        assert len(history["events"]) == 1

        # get_technical_asset_history should fail
        response = self.get_technical_asset_history(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 404

    def test_retain_deleted_technical_asset_name_in_history(self, client):
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__DELETE_TECHNICAL_ASSET],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        technical_asset = TechnicalAssetFactory(owner=data_product)
        technical_asset_name = technical_asset.name

        response = self.delete_technical_asset(
            client, technical_asset.owner.id, technical_asset.id
        )
        assert response.status_code == 200

        response = self.get_data_product_history(client, technical_asset.owner.id)
        assert len(response.json()["events"]) == 1
        assert (
            response.json()["events"][0]["deleted_subject_identifier"]
            == technical_asset_name
        )

    @patch("app.data_products.technical_assets.email.send_link_output_port_email")
    def test_dataset_link_auto_approval_no_email_sent(
        self, mock_send_email, client: TestClient
    ):
        """Test that no email is sent when dataset link request is auto-approved"""
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        data_product = DataProductFactory()
        dataset = OutputPortFactory(data_product=data_product)
        technical_asset = TechnicalAssetFactory(owner=data_product)

        # Create role that allows linking datasets
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )

        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        ds_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(
            user_id=user.id, role_id=ds_role.id, output_port_id=dataset.id
        )
        # Mock auto-approval scenario (same data product owner)
        response = client.post(
            f"{TECHNICAL_ASSETS_OUTPUT_PORTS_ENDPOINT.format(data_product.id, dataset.id)}/add",
            json={"technical_asset_id": f"{technical_asset.id}"},
        )

        assert response.status_code == 200
        # Verify no email was sent for auto-approved request
        mock_send_email.assert_not_called()

    @patch("app.data_products.technical_assets.email.send_link_output_port_email")
    def test_dataset_link_manual_approval_email_sent(
        self, mock_send_email, client: TestClient
    ):
        """Test that email is sent when dataset link request requires manual approval"""
        user = UserFactory(external_id=settings.DEFAULT_USERNAME)
        other_approver = UserFactory()
        data_product = DataProductFactory()
        dataset = OutputPortFactory(data_product=data_product)  # Different owner
        technical_asset = TechnicalAssetFactory(owner=data_product)

        # Create role that allows linking datasets
        role = RoleFactory(
            scope=Scope.DATA_PRODUCT,
            permissions=[Action.DATA_PRODUCT__REQUEST_TECHNICAL_ASSET_LINK],
        )
        DataProductRoleAssignmentFactory(
            identity_id=user.id, role_id=role.id, data_product_id=data_product.id
        )
        approver_role = RoleFactory(
            scope=Scope.DATASET,
            permissions=[Action.OUTPUT_PORT__APPROVE_TECHNICAL_ASSET_LINK_REQUEST],
        )
        DatasetRoleAssignmentFactory(
            user_id=other_approver.id,
            role_id=approver_role.id,
            output_port_id=dataset.id,
        )

        # Mock manual approval scenario (different data product owner)
        response = client.post(
            f"{TECHNICAL_ASSETS_OUTPUT_PORTS_ENDPOINT.format(data_product.id, dataset.id)}/add",
            json={"technical_asset_id": f"{technical_asset.id}"},
        )

        assert response.status_code == 200
        # Verify email was sent for manual approval request
        mock_send_email.assert_called_once()

    @staticmethod
    def delete_technical_asset(
        client: TestClient, data_product_id, technical_asset_id
    ) -> Response:
        return client.delete(f"{ENDPOINT.format(data_product_id)}/{technical_asset_id}")

    @staticmethod
    def create_technical_asset(
        client: TestClient, default_technical_asset_payload
    ) -> Response:
        return client.post(
            f"/api/v2/data_products/{default_technical_asset_payload.get('owner_id')}/technical_assets",
            json=default_technical_asset_payload,
        )

    @staticmethod
    def get_technical_asset(
        client: TestClient, data_product_id, technical_asset_id
    ) -> Response:
        return client.get(f"{ENDPOINT.format(data_product_id)}/{technical_asset_id}")

    @staticmethod
    def update_technical_asset(
        client: TestClient, payload, data_product_id, technical_asset_id
    ) -> Response:
        return client.put(
            f"{ENDPOINT.format(data_product_id)}/{technical_asset_id}", json=payload
        )

    @staticmethod
    def update_technical_asset_status(
        client: TestClient, status, data_product_id, technical_asset_id
    ) -> Response:
        return client.put(
            f"{ENDPOINT.format(data_product_id)}/{technical_asset_id}/status",
            json=status,
        )

    @staticmethod
    def get_namespace_suggestion(client: TestClient, name) -> Response:
        return client.get(f"/api/v2/resource_names/sanitize?name={name}")

    @staticmethod
    def get_namespace_validation(
        client: TestClient, namespace, data_product_id
    ) -> Response:
        return client.get(
            "/api/v2/resource_names/validate",
            params={
                "resource_name": namespace,
                "model": "technical_asset",
                "data_product_id": data_product_id,
            },
        )

    @staticmethod
    def get_namespace_length_limits(client: TestClient) -> Response:
        return client.get("/api/v2/resource_names/constraints")

    @staticmethod
    def get_technical_asset_history(client, data_product_id, technical_asset_id):
        return client.get(
            f"{ENDPOINT.format(data_product_id)}/{technical_asset_id}/history"
        )

    @staticmethod
    def get_data_product_history(client, data_product_id):
        return client.get(f"/api/v2/data_products/{data_product_id}/history")


@pytest.fixture
def ta_event_payload():
    service = PlatformServiceFactory()
    tag = TagFactory()
    return {
        "name": "Test Asset",
        "description": "desc",
        "namespace": "test-ta-event-ns",
        "technical_mapping": "default",
        "configuration": {
            "path": "test",
            "name": "FakeTechnicalAssetConfiguration",
        },
        "platform_id": str(service.platform.id),
        "service_id": str(service.id),
        "tag_ids": [str(tag.id)],
    }


class TestTechnicalAssetsRouterV2Events:
    @staticmethod
    def _ta_endpoint(dp_id):
        return ENDPOINT.format(dp_id)

    @staticmethod
    def _link_endpoint(dp_id, op_id):
        return f"/api/v2/data_products/{dp_id}/output_ports/{op_id}/technical_assets"
