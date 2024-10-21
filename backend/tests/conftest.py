import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, scoped_session

from app.data_product_memberships.model import DataProductUserRole
from app.database.database import Base, get_db_session
from app.datasets.enums import DatasetAccessType
from app.main import app

from . import TestingSessionLocal
from .factories.business_area import BusinessAreaFactory
from .factories.data_product_type import DataProductTypeFactory
from .factories.user import UserFactory


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_database():

    from app.db_tool import init  # noqa: E402

    init(True, False)
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


@pytest.fixture
def client():
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()


@pytest.fixture
def default_data_product_payload():
    data_product_type = DataProductTypeFactory()
    user = UserFactory()
    business_area = BusinessAreaFactory()
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
        "business_area_id": str(business_area.id),
    }


@pytest.fixture
def default_dataset_payload():
    user = UserFactory()
    business_area = BusinessAreaFactory()
    return {
        "name": "Test Dataset",
        "description": "Test Description",
        "external_id": "test-dataset",
        "tags": [],
        "owners": [str(user.id)],
        "access_type": DatasetAccessType.RESTRICTED,
        "business_area_id": str(business_area.id),
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
