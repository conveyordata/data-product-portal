import factory

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignmentModel,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.authz.authorization import Authorization
from tests import test_session


class DataProductRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DataProductRoleAssignmentModel

    id = factory.Faker("uuid4")
    data_product_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    role_id = factory.Faker("uuid4")
    decision = DecisionStatus.APPROVED

    @factory.post_generation
    def sync_role(self, create, extracted, **kwargs):
        if self.decision == DecisionStatus.APPROVED:
            authorizer = Authorization()
            authorizer.assign_resource_role(
                role_id=str(self.role_id),
                user_id=str(self.user_id),
                resource_id=str(self.data_product_id),
            )
            test_session.commit()
