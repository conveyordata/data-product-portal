import factory

from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.enums import DecisionStatus


class DataProductRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductRoleAssignment

    id = factory.Faker("uuid4")
    data_product_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    role_id = factory.Faker("uuid4")
    decision = DecisionStatus.PENDING
