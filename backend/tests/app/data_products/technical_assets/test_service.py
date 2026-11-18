import threading

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data_products.technical_assets.schema_request import (
    CreateTechnicalAssetRequest,
)
from app.data_products.technical_assets.service import TechnicalAssetService
from tests import session_factory
from tests.factories import DataProductFactory, PlatformServiceFactory


def test_create_technical_asset__concurrent_duplicate_namespace(session: Session):
    data_product = DataProductFactory()
    service = PlatformServiceFactory()
    session.commit()  # noqa: allow-commit
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

    TechnicalAssetService(first).create_technical_asset(data_product.id, request)
    thread = threading.Thread(target=create_second)
    thread.start()
    thread.join(timeout=1)
    assert thread.is_alive(), "second create should wait for the first to finish"

    first.commit()  # noqa: allow-commit
    first.close()
    thread.join(timeout=10)

    assert not thread.is_alive()
    assert len(errors) == 1
    assert errors[0].status_code == 400
    assert "DUPLICATE" in errors[0].detail
