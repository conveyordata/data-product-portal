from typing import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.business_areas.model import BusinessArea as BusinessAreaModel
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.data_product_memberships.model import DataProductUserRole
from app.data_product_types.model import DataProductType as DataProductTypeModel
from app.data_products.model import DataProduct as DataProductModel
from app.database.database import get_db_session
from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset as DatasetModel
from app.environments.schema import Environment as EnvironmentModel
from app.main import app
from app.settings import settings
from app.users.model import User as UserModel

# Set up a test client using the FastAPI app
test_client = TestClient(app)


def get_test_url():
    return (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


engine = create_engine(get_test_url(), connect_args={})

#  Create a clean database on each test run
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_database():

    from app.db_tool import init  # noqa: E402

    init(True, False)
    yield


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    db_session = TestingSessionLocal(bind=connection)

    yield db_session

    db_session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db_session] = override_get_db
    yield test_client
    del app.dependency_overrides[get_db_session]


@pytest.fixture()
def default_business_area(session):
    business_area = BusinessAreaModel(
        name="Test Business Area",
        description="Test Description",
    )

    session.add(business_area)
    session.commit()
    session.refresh(business_area)
    return business_area


@pytest.fixture()
def default_user_model_payload():
    return UserModel(
        id=UUID("756aa810-168d-4940-a2b9-c9f3a8b1f9c4"),
        email="test@test.be",
        external_id="sub",
        first_name="test",
        last_name="test",
    )


@pytest.fixture()
def default_user(session, default_user_model_payload):
    session.add(default_user_model_payload)
    session.commit()
    session.refresh(default_user_model_payload)
    return default_user_model_payload


@pytest.fixture()
def default_data_product_type(session):
    data_product_type = DataProductTypeModel(
        name="Test Data Product Type",
        description="Test Description",
    )

    session.add(data_product_type)
    session.commit()
    session.refresh(data_product_type)
    return data_product_type


@pytest.fixture()
def default_secondary_user(session):
    data = UserModel(
        id=UUID("c9f3a8b1f9c4-168d-4940-a2b9-756aa810"),
        email="test2@test.be",
        external_id="sub2",
        first_name="test2",
        last_name="test2",
    )
    session.add(data)
    session.commit()
    session.refresh(data)
    return data


@pytest.fixture()
def default_data_product_membership(session, default_user, default_data_product_type):
    data_product_membership = DataProductMembershipModel(
        user_id=default_user.id,
        role=DataProductUserRole.OWNER,
    )
    return data_product_membership


@pytest.fixture()
def default_data_product(
    session,
    default_data_product_type,
    default_business_area,
    default_data_product_membership,
):
    data_product = DataProductModel(
        name="Test Data Product",
        description="Test Description",
        external_id="test-data_product",
        type_id=default_data_product_type.id,
        memberships=[
            default_data_product_membership,
        ],
        business_area_id=default_business_area.id,
        tags=[],
    )
    return data_product


@pytest.fixture()
def default_data_product_payload(
    default_data_product,
    default_user,
):
    return {
        "name": default_data_product.name,
        "description": default_data_product.description,
        "external_id": str(default_data_product.external_id),
        "tags": default_data_product.tags,
        "type_id": str(default_data_product.type_id),
        "memberships": [
            {
                "user_id": str(default_user.id),
                "role": DataProductUserRole.OWNER.value,
            }
        ],
        "business_area_id": str(default_data_product.business_area_id),
    }


@pytest.fixture()
def default_dataset(
    session,
    default_business_area,
    default_user,
):
    dataset = DatasetModel(
        name="Test Dataset",
        external_id="test-dataset",
        description="Test Description",
        tags=[],
        access_type=DatasetAccessType.PUBLIC,
        owners=[default_user],
        business_area_id=default_business_area.id,
    )
    return dataset


@pytest.fixture()
def default_dataset_payload(
    default_dataset,
):
    return {
        "name": default_dataset.name,
        "description": default_dataset.description,
        "external_id": default_dataset.external_id,
        "tags": [],
        "owners": [
            str(default_dataset.owners[0].id),
        ],
        "access_type": DatasetAccessType.RESTRICTED,
        "business_area_id": str(default_dataset.business_area_id),
    }


@pytest.fixture()
def default_environments(
    session,
):
    return [
        EnvironmentModel(
            name="development",
            context="dev",
            is_default=True,
        ),
        EnvironmentModel(
            name="production",
            context="prod",
        ),
    ]
