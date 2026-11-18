from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from starlette.testclient import TestClient

from app.resource_names.router import validate_resource_name
from app.resource_names.service import ResourceNameValidityType
from tests.factories import (
    DataProductFactory,
    DomainFactory,
    ExplorationFactory,
    SizingTechnicalAssetConfigurationFactory,
    TechnicalAssetFactory,
)


class TestResourceNamesRouter:
    @staticmethod
    def validate_namespace(client: TestClient, namespace: str, model: str):
        return client.get(
            "api/v2/resource_names/validate",
            params={"resource_name": namespace, "model": model},
        )

    @staticmethod
    def validate_technical_asset_namespace(
        client: TestClient,
        namespace: str,
        data_product_id: str,
        technical_asset_type: str = "FakeTechnicalAssetConfiguration",
    ):
        return client.get(
            "api/v2/resource_names/validate",
            params={
                "resource_name": namespace,
                "model": "technical_asset",
                "data_product_id": data_product_id,
                "technical_asset_type": technical_asset_type,
            },
        )

    def test_validate_resource_name__technical_asset(self, client: TestClient):
        data_product = DataProductFactory()
        response = self.validate_technical_asset_namespace(
            client, "valid-namespace", str(data_product.id)
        )

        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.VALID

    def test_validate_resource_name__technical_asset_duplicate_same_type(
        self, client: TestClient
    ):
        technical_asset = TechnicalAssetFactory()
        response = self.validate_technical_asset_namespace(
            client, technical_asset.namespace, str(technical_asset.owner.id)
        )

        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.DUPLICATE

    def test_validate_resource_name__technical_asset_duplicate_other_type(
        self, client: TestClient
    ):
        technical_asset = TechnicalAssetFactory(
            configuration=SizingTechnicalAssetConfigurationFactory()
        )
        response = self.validate_technical_asset_namespace(
            client, technical_asset.namespace, str(technical_asset.owner.id)
        )

        assert response.status_code == 200
        assert response.json()["validity"] == ResourceNameValidityType.VALID

    def test_validate_resource_name__technical_asset_unknown_type(
        self, client: TestClient
    ):
        data_product = DataProductFactory()
        response = self.validate_technical_asset_namespace(
            client, "valid-namespace", str(data_product.id), "UnknownType"
        )

        assert response.status_code == 422

    def test_validate_resource_name__technical_asset_missing_type(
        self, client: TestClient
    ):
        data_product = DataProductFactory()
        response = client.get(
            "api/v2/resource_names/validate",
            params={
                "resource_name": "valid-namespace",
                "model": "technical_asset",
                "data_product_id": str(data_product.id),
            },
        )

        assert response.status_code == 400

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
