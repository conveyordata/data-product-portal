import factory

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.model import DataProductMembership

from .data_product import DataProductFactory
from .user import UserFactory


class DataProductMembershipFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductMembership

    id = factory.Faker("uuid4")
    role = DataProductUserRole.OWNER.value
    status = DataProductMembershipStatus.APPROVED.value
    user = factory.SubFactory(UserFactory)
    data_product = factory.SubFactory(DataProductFactory)
    requested_by_id = None
