import factory

from app.abstract_data_product.input_ports.enums import InputPortRequestDecision
from app.abstract_data_product.input_ports.model import (
    InputPortRequest,
)
from app.access_durations.enums import AccessDurationType

from .input_port import InputPortFactory
from .user import UserFactory


class InputPortRequestFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InputPortRequest

    id = factory.Faker("uuid4")
    decision = InputPortRequestDecision.APPROVED
    justification = factory.Faker("text", max_nb_chars=20)
    decision_note = factory.Faker("text", max_nb_chars=20)
    access_duration_type = AccessDurationType.PERMANENT
    input_port = factory.SubFactory(InputPortFactory, request=False)
    requested_by = factory.SubFactory(UserFactory)
    decided_by = factory.LazyAttribute(
        lambda o: (
            UserFactory() if o.decision != InputPortRequestDecision.PENDING else None
        )
    )
