from datetime import datetime, timezone

import factory

from app.abstract_data_product.input_ports.model import (
    InputPort,
)
from app.authorization.role_assignments.enums import DecisionStatus

from .data_product import DataProductFactory
from .dataset import DatasetFactory
from .user import UserFactory


class InputPortFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InputPort

    id = factory.Faker("uuid4")
    justification = factory.Faker("text", max_nb_chars=20)
    decision_note = factory.Faker("text", max_nb_chars=20)
    status = DecisionStatus.APPROVED
    consuming_abstract_data_product = factory.SubFactory(DataProductFactory)
    dataset = factory.SubFactory(DatasetFactory)
    requested_by = factory.SubFactory(UserFactory)
    created_on = factory.LazyFunction(lambda: datetime.now(timezone.utc))
