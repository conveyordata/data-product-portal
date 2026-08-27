import json

import pytest
from pydantic_core import PydanticSerializationError

from app.abstract_data_product.schema_response import AbstractDataProductInfo
from app.abstract_data_product.type import AbstractDataProductType
from app.core.authz import REDACTION_VALUE


def test_abstract_data_product_info__redacted_not_set_fails_serialisation():
    adp = AbstractDataProductInfo(
        name="test",
        namespace="test",
        abstract_data_product_type=AbstractDataProductType.EXPLORATION,
    )

    with pytest.raises(PydanticSerializationError, match="is_redacted must be set"):
        adp.model_dump_json()


def test_abstract_data_product_info__json_serialisation_redacts():
    adp = AbstractDataProductInfo(
        name="test",
        namespace="test",
        abstract_data_product_type=AbstractDataProductType.EXPLORATION,
    )
    adp.set_redacted(True)

    assert json.loads(adp.model_dump_json())["name"] == REDACTION_VALUE


def test_abstract_data_product_info__does_not_redact_when_no_redacted():
    adp = AbstractDataProductInfo(
        name="test",
        namespace="test",
        abstract_data_product_type=AbstractDataProductType.EXPLORATION,
    )
    adp.set_redacted(False)

    assert json.loads(adp.model_dump_json())["name"] == adp.name
