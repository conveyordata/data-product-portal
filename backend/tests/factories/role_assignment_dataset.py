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
        # Exclude `output_port` so it is consumed here and NOT forwarded to the model
        # constructor (the model uses output_port_id / data_product_id scalar columns).
        exclude = ["output_port"]

    id = factory.Faker("uuid4")

    # Callers may pass either:
    #   output_port=<OutputPort object>  — derive output_port_id & data_product_id from it
    #   output_port_id=<UUID>         — look up the dataset from the session for data_product_id
    output_port = None
    output_port_id = factory.LazyAttribute(
        lambda o: o.output_port.id if o.output_port is not None else uuid.uuid4()
    )
    data_product_id = factory.LazyAttribute(
        lambda o: (
            o.output_port.data_product_id
            if o.output_port is not None
            else (
                _ds.data_product_id
                if (_ds := test_session.get(Dataset, o.output_port_id)) is not None
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
                resource_id=str(self.output_port_id),
            )
            test_session.commit()
