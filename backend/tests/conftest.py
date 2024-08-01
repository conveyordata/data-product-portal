from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.business_areas.model import BusinessArea as BusinessAreaModel
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.data_product_memberships.model import DataProductUserRole
from app.data_product_types.model import DataProductType as DataProductTypeModel
from app.data_products.model import DataProduct as DataProductModel
from app.database.database import Base, get_db_session
from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset as DatasetModel
from app.environments.schema import Environment as EnvironmentModel
from app.main import app
from app.users.model import User as UserModel

from . import TestingSessionLocal
from .factories import UserFactory


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


@pytest.fixture()
def client():
    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
        app.dependency_overrides.clear()


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
def admin_user_model_payload():
    return UserModel(
        id=UUID("756aa810-168d-4940-a2b9-c9f3a8b1f777"),
        email="john.doe@dataminded.com",
        external_id="admin",
        first_name="admin",
        last_name="test",
        is_admin=True,
    )


@pytest.fixture()
def default_user(session, default_user_model_payload):
    session.add(default_user_model_payload)
    session.commit()
    session.refresh(default_user_model_payload)
    return default_user_model_payload


@pytest.fixture()
def admin_user(session, admin_user_model_payload):
    session.add(admin_user_model_payload)
    session.commit()
    session.refresh(admin_user_model_payload)
    return admin_user_model_payload


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


@pytest.fixture
def admin_data_product_membership(session, admin_user):
    data_product_membership = DataProductMembershipModel(
        user_id=admin_user.id,
        role=DataProductUserRole.MEMBER,
    )
    return data_product_membership


@pytest.fixture
def admin_data_product(
    session,
    default_data_product_type,
    default_business_area,
    admin_data_product_membership,
):
    data_product = DataProductModel(
        name="Test Data Product",
        description="Test Description",
        external_id="test-data_product",
        type_id=default_data_product_type.id,
        memberships=[
            admin_data_product_membership,
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


@pytest.fixture
def admin_dataset(
    session,
    default_business_area,
    admin_user,
):
    dataset = DatasetModel(
        name="Test Dataset",
        external_id="test-dataset",
        description="Test Description",
        tags=[],
        access_type=DatasetAccessType.PUBLIC,
        owners=[admin_user],
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
def admin_dataset_payload(
    admin_dataset,
):
    return {
        "name": admin_dataset.name,
        "description": admin_dataset.description,
        "external_id": admin_dataset.external_id,
        "tags": [],
        "owners": [
            str(admin_dataset.owners[0].id),
        ],
        "access_type": DatasetAccessType.RESTRICTED,
        "business_area_id": str(admin_dataset.business_area_id),
    }


@pytest.fixture()
def default_environments(session):
    return [
        EnvironmentModel(
            name="development",
            context="test_context_{{}}",
            is_default=True,
        ),
        EnvironmentModel(name="production", context="test_context_{{}}"),
    ]


@pytest.fixture(autouse=True)
def clear_db(session: TestingSessionLocal) -> None:
    """Clear database after each test."""
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture
def admin():
    return UserFactory(external_id="sub", is_admin=True)
