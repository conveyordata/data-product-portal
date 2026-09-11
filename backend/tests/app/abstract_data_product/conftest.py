import pytest

from app.abstract_data_product.service import AbstractDataProductService
from tests.factories import UserFactory
from tests.session_util import as_user


@pytest.fixture(autouse=True)
def abstract_data_product_service(session):
    with as_user(session, UserFactory().id):
        yield AbstractDataProductService(db=session)
