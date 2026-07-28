from datetime import datetime, timezone

import factory

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
)
from app.abstract_data_product.input_ports.model import (
    InputPort,
)

from .data_product import DataProductFactory
from .dataset import OutputPortFactory
from .user import UserFactory


class InputPortFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = InputPort

    id = factory.Faker("uuid4")
    status = InputPortStatus.APPROVED
    consuming_abstract_data_product = factory.SubFactory(DataProductFactory)
    output_port = factory.SubFactory(OutputPortFactory)

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

        if obj.status == InputPortStatus.CANCELLED:
            decision = InputPortRequestDecision.CANCELLED
        elif obj.status in (InputPortStatus.EXPIRED, InputPortStatus.REVOKED):
            decision = InputPortRequestDecision.APPROVED
        else:
            decision = InputPortRequestDecision(obj.status.value)
        kwargs.setdefault("decision", decision)
        if obj.status == InputPortStatus.REVOKED:
            kwargs.setdefault("revoked_at", datetime.now(timezone.utc))
            kwargs.setdefault("revoked_by", UserFactory())
        InputPortRequestFactory(input_port=obj, **kwargs)
