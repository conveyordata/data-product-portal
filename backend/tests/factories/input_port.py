import factory

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.input_ports.model import (
    InputPort,
)
from app.authorization.role_assignments.enums import DecisionStatus

from .data_product import DataProductFactory
from .dataset import OutputPortFactory


class InputPortFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InputPort

    id = factory.Faker("uuid4")
    status = InputPortStatus.APPROVED
    consuming_abstract_data_product = factory.SubFactory(DataProductFactory)
    dataset = factory.SubFactory(OutputPortFactory)

    @factory.post_generation
    def request(obj, create, extracted, **kwargs):
        """
        A request is automatically created for the input port you create.
        Set the attributes of the request following this pattern:
        `InputPortFactory(request__requested_by=UserFactory())`
        """

        if not create or extracted is False:
            return
        from .input_port_request import InputPortRequestFactory

        decision = (
            DecisionStatus.APPROVED
            if obj.status == InputPortStatus.EXPIRED
            else DecisionStatus(obj.status.value)
        )
        kwargs.setdefault("decision", decision)
        InputPortRequestFactory(input_port=obj, **kwargs)
