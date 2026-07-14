import factory

from app.abstract_data_product.input_ports.model import (
    InputPortRequest,
)
from app.access_durations.enums import AccessDurationType
from app.authorization.role_assignments.enums import DecisionStatus

from .input_port import InputPortFactory
from .user import UserFactory


class InputPortRequestFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InputPortRequest

    id = factory.Faker("uuid4")
    decision = DecisionStatus.APPROVED
    justification = factory.Faker("text", max_nb_chars=20)
    decision_note = factory.Faker("text", max_nb_chars=20)
    access_duration_type = AccessDurationType.PERMANENT
    input_port = factory.SubFactory(InputPortFactory, request=False)
    requested_by = factory.SubFactory(UserFactory)
    decided_by = factory.LazyAttribute(
        lambda o: UserFactory() if o.decision != DecisionStatus.PENDING else None
    )
