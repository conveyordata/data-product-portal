import threading

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_products.technical_assets.model import TechnicalAsset
from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
)
from app.data_products.technical_assets.service import TechnicalAssetService
from app.technical_asset_configuration.base_model import TechnicalAssetConfiguration
from tests import session_factory
from tests.factories import (
    DataProductFactory,
    PlatformServiceFactory,
    TechnicalAssetFactory,
)


class TestTechnicalAssetService:
    def test_remove_technical_asset__deletes_configuration(self, session):
        technical_asset = TechnicalAssetFactory()
        technical_asset_id = technical_asset.id
        configuration_id = technical_asset.configuration_id
        configuration_type = type(technical_asset.configuration)

        TechnicalAssetService(session).remove_technical_asset(
            technical_asset.owner_id, technical_asset_id
        )

        assert session.get(TechnicalAsset, technical_asset_id) is None
        assert session.get(configuration_type, configuration_id) is None
        assert session.get(TechnicalAssetConfiguration, configuration_id) is None


@pytest.mark.commits
def test_create_technical_asset__concurrent_duplicate_namespace(session: Session):
    data_product = DataProductFactory()
    service = PlatformServiceFactory()
    session.commit()  # allow-commit
    request = CreateTechnicalAssetRequest.model_validate(
        {
            "name": "Orders",
            "description": "Orders",
            "namespace": "orders",
            "technical_mapping": "custom",
            "configuration": {
                "path": "orders",
                "name": "FakeTechnicalAssetConfiguration",
            },
            "platform_id": str(service.platform.id),
            "service_id": str(service.id),
            "tag_ids": [],
        }
    )
    first, second = session_factory(), session_factory()
    errors: list[HTTPException] = []

    def create_second():
        try:
            TechnicalAssetService(second).create_technical_asset(
                data_product.id, request
            )
        except HTTPException as error:
            errors.append(error)
        finally:
            second.rollback()
            second.close()

    thread = threading.Thread(target=create_second)
    try:
        TechnicalAssetService(first).create_technical_asset(data_product.id, request)
        thread.start()
        thread.join(timeout=1)
        assert thread.is_alive(), "second create should wait for the first to finish"
        first.commit()  # allow-commit
    finally:
        first.close()
        if thread.ident is None:
            second.close()
        thread.join(timeout=10)

    assert not thread.is_alive()
    assert len(errors) == 1
    assert errors[0].status_code == 400
    assert "DUPLICATE" in errors[0].detail
