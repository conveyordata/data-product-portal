from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from app.resource_names.router import validate_resource_name
from app.resource_names.service import ResourceNameValidityType
from app.settings import settings
from tests.factories import (
    DataProductFactory,
    DomainFactory,
    ExplorationFactory,
    TechnicalAssetFactory,
)
from tests.fixtures.fake_plugin.schema import FakeTechnicalAssetConfiguration
from tests.fixtures.sizing_plugin.model import NAME as SIZING_PLUGIN


class TestResourceNamesRouter:
    @staticmethod
    def validate_namespace(client: TestClient, namespace: str, model: str):
        return client.get(
            "api/v2/resource_names/validate",
            params={"resource_name": namespace, "model": model},
        )

    def test_validated_exploration(self, client):
        namespace = "test"
        response = self.validate_namespace(client, namespace, "exploration")
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.VALID

    def test_validate_exploration_duplicate_namespaces(self, client: TestClient):
        namespace = "namespace"
        ExplorationFactory(namespace=namespace)

        response = self.validate_namespace(client, namespace, "exploration")
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE

    def test_validate_resource_name__duplicate_domain_namespace(
        self, client: TestClient
    ):
        namespace = "finance"
        DomainFactory(namespace=namespace)

        response = self.validate_namespace(client, namespace, "domain")
        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE

    @pytest.mark.parametrize("namespace", [".", "..", "..."])
    def test_validate_resource_name__dots_only_domain_namespace(
        self, client: TestClient, namespace
    ):
        response = self.validate_namespace(client, namespace, "domain")
        assert response.json()["validity"] == (
            ResourceNameValidityType.INVALID_CHARACTERS
        )

    def test_validate_resource_name__trailing_newline(self, client: TestClient):
        response = self.validate_namespace(client, "finance\n", "domain")
        assert response.json()["validity"] == (
            ResourceNameValidityType.INVALID_CHARACTERS
        )

    @pytest.mark.parametrize("name", ["...", "-..-"])
    def test_sanitize_resource_name__dots_only_suggests_nothing(
        self, client: TestClient, name
    ):
        response = client.get("api/v2/resource_names/sanitize", params={"name": name})
        assert response.json()["resource_name"] == ""

    def test_validate_resource_name(self):
        """
        This test exists to ensure the case is tested where we have added a new model to the enum
        but forgot to implement it. This ensures we have 100% coverage of this router
        """
        with pytest.raises(HTTPException):
            validate_resource_name("bla", "unknown model", db=MagicMock())  # type: ignore[arg-type]

    @pytest.mark.parametrize("limit", [None, 24, 96])
    def test_technical_asset_namespace__uses_plugin_length_or_default(
        self, client, monkeypatch, limit
    ):
        if limit is not None:
            monkeypatch.setattr(
                FakeTechnicalAssetConfiguration,
                "_platform_metadata",
                FakeTechnicalAssetConfiguration.get_platform_metadata().model_copy(
                    update={"namespace_max_length": limit}
                ),
            )
        expected_limit = settings.NAMESPACE_MAX_LENGTH if limit is None else limit
        asset_type = FakeTechnicalAssetConfiguration.name
        response = client.get(
            "/api/v2/resource_names/sanitize",
            params={
                "name": "a" * (expected_limit + 1),
                "technical_asset_type": asset_type,
            },
        )
        assert response.status_code == 200
        assert response.json()["resource_name"] == "a" * expected_limit

        product = DataProductFactory()
        for length, expected in [
            (expected_limit, ResourceNameValidityType.VALID),
            (expected_limit + 1, ResourceNameValidityType.INVALID_LENGTH),
        ]:
            response = client.get(
                "/api/v2/resource_names/validate",
                params={
                    "resource_name": "a" * length,
                    "model": "technical_asset",
                    "data_product_id": str(product.id),
                    "technical_asset_type": asset_type,
                },
            )
            assert response.status_code == 200
            assert response.json()["validity"] == expected

    @pytest.mark.parametrize(
        ("same_product", "asset_type", "expected"),
        [
            (
                True,
                FakeTechnicalAssetConfiguration.name,
                ResourceNameValidityType.DUPLICATE,
            ),
            (True, SIZING_PLUGIN, ResourceNameValidityType.VALID),
            (
                False,
                FakeTechnicalAssetConfiguration.name,
                ResourceNameValidityType.VALID,
            ),
        ],
    )
    def test_validate_resource_name__scopes_namespace_to_type_and_product(
        self, client, same_product, asset_type, expected
    ):
        asset = TechnicalAssetFactory(namespace="orders")
        product = asset.owner if same_product else DataProductFactory()

        response = client.get(
            "/api/v2/resource_names/validate",
            params={
                "resource_name": "orders",
                "model": "technical_asset",
                "data_product_id": str(product.id),
                "technical_asset_type": asset_type,
            },
        )

        assert response.status_code == 200
        assert response.json()["validity"] == expected

    @pytest.mark.parametrize("missing", ["technical_asset_type", "data_product_id"])
    def test_validate_resource_name__requires_technical_asset_scope(
        self, client, missing
    ):
        params = {
            "resource_name": "orders",
            "model": "technical_asset",
            "data_product_id": str(DataProductFactory().id),
            "technical_asset_type": FakeTechnicalAssetConfiguration.name,
        }
        params.pop(missing)

        response = client.get("/api/v2/resource_names/validate", params=params)

        assert response.status_code == 422

    def test_sanitize_resource_name__rejects_unknown_type(self, client):
        response = client.get(
            "/api/v2/resource_names/sanitize",
            params={"name": "orders", "technical_asset_type": "UnknownPlugin"},
        )

        assert response.status_code == 400
