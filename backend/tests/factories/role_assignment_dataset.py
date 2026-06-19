import uuid

import factory

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import DatasetRoleAssignment
from app.core.authz.authorization import Authorization
from app.data_products.output_ports.model import Dataset
from tests import test_session


class DatasetRoleAssignmentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DatasetRoleAssignment
        # Exclude `dataset` so it is consumed here and NOT forwarded to the model
        # constructor (the model uses dataset_id / data_product_id scalar columns).
        exclude = ["dataset"]

    id = factory.Faker("uuid4")

    # Callers may pass either:
    #   dataset=<Dataset object>  — derive dataset_id & data_product_id from it
    #   dataset_id=<UUID>         — look up the dataset from the session for data_product_id
    dataset = None
    dataset_id = factory.LazyAttribute(
        lambda o: o.dataset.id if o.dataset is not None else uuid.uuid4()
    )
    data_product_id = factory.LazyAttribute(
        lambda o: (
            o.dataset.data_product_id
            if o.dataset is not None
            else (
                _ds.data_product_id
                if (_ds := test_session.get(Dataset, o.dataset_id)) is not None
                else uuid.uuid4()
            )
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
