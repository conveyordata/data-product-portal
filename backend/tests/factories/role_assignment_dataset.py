import factory

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import DatasetRoleAssignment
from app.core.authz.authorization import Authorization
from app.data_products.output_ports.model import Dataset
from tests import test_session


class DatasetRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DatasetRoleAssignment
        exclude = ["_dataset"]

    id = factory.Faker("uuid4")
    dataset_id = factory.Faker("uuid4")
    # Resolve data_product_id by looking up the dataset from the session.
    # Works whether callers pass dataset_id= directly or leave it random.
    _dataset = factory.LazyAttribute(lambda o: test_session.get(Dataset, o.dataset_id))
    data_product_id = factory.LazyAttribute(
        lambda o: (
            o._dataset.data_product_id
            if o._dataset is not None
            else factory.Faker("uuid4").generate()
        )
    )
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
                resource_id=str(self.dataset_id),
            )
            test_session.commit()
