import pytest
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.data_products.output_ports.model import OutputPort
from tests.factories import OutputPortFactory


def test_access_function_must_match_access_type(session):
    output_port = OutputPortFactory(access_function=OutputPortAccessFunction.PRIVATE)

    with pytest.raises(IntegrityError), session.begin_nested():
        session.execute(
            update(OutputPort)
            .where(OutputPort.id == output_port.id)
            .values(access_function=OutputPortAccessFunction.UNRESTRICTED)
        )
