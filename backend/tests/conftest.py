from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, scoped_session

from app.core.auth.device_flows.service import verify_auth_header
from app.data_product_memberships.model import DataProductUserRole
from app.database.database import Base, get_db_session
from app.datasets.enums import DatasetAccessType
from app.main import app

from . import TestingSessionLocal
from .factories.data_product_type import DataProductTypeFactory
from .factories.domain import DomainFactory
from .factories.user import UserFactory


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_database():
    from app.db_tool import init  # noqa: E402

    init(force=True)
    yield


def override_get_db():
    test_db = None
    try:
        test_db = TestingSessionLocal()
        yield test_db
        test_db.commit()
    finally:
        if test_db:
            test_db.close()


session = pytest.fixture(override_get_db)

from app.core.auth import jwt  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def mock_oidc_config():
    """Mock OIDCConfiguration globally before any test runs."""
    mock_instance = MagicMock()
    mock_instance.client_id = "test_client_id"
    mock_instance.client_secret = "test_client_secret"
    mock_instance.redirect_uri = "http://test-redirect-uri"
    mock_instance.token_endpoint = "http://test-token-endpoint"
    mock_instance.authorization_endpoint = "http://test-authorization-endpoint"
    mock_instance.provider.name = "test-provider"
    # Force override the existing instance in `jwt.py`
    jwt.oidc = mock_instance


@pytest.fixture
def client():
    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[verify_auth_header] = (
        lambda: "8cb30dd2-4e3e-4284-a71e-5dbe8e2bdb69"
    )
    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()


@pytest.fixture
def default_data_product_payload():
    data_product_type = DataProductTypeFactory()
    user = UserFactory()
    domain = DomainFactory()
    return {
        "name": "Test Data Product",
        "description": "Test Description",
        "external_id": "test-data_product",
        "tags": [],
        "type_id": str(data_product_type.id),
        "memberships": [
            {
                "user_id": str(user.id),
                "role": DataProductUserRole.OWNER.value,
            }
        ],
        "domain_id": str(domain.id),
    }


@pytest.fixture
def default_dataset_payload():
    user = UserFactory()
    domain = DomainFactory()
    return {
        "name": "Test Dataset",
        "description": "Test Description",
        "external_id": "test-dataset",
        "tags": [],
        "owners": [str(user.id)],
        "access_type": DatasetAccessType.RESTRICTED,
        "domain_id": str(domain.id),
    }


@pytest.fixture(autouse=True)
def clear_db(session: scoped_session[Session]) -> None:
    """Clear database after each test."""
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture
def admin():
    return UserFactory(external_id="sub", is_admin=True)
