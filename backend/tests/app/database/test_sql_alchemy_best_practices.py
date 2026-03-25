import pytest
from sqlalchemy import inspect

from app.database.database import Base

models = [mapper.class_ for mapper in Base.registry.mappers]

# The purpose of this list is to ensure we don't have to fix everything all at once
# We can ignore our tech debt for now and improve it later, but we won't make it worse
ignore_list = {
    "TechnicalAsset": ["tags"],
    "Platform": ["services"],
    "User": ["data_product_roles", "dataset_roles"],
    "Dataset": ["tags"],
    "DataProduct": ["tags"],
}


@pytest.mark.parametrize("model", models)
def test_many_relationships_use_lazy_raise(model):
    mapper = inspect(model)

    for relationship in mapper.relationships:
        if (
            model.__name__ in ignore_list
            and relationship.key in ignore_list[model.__name__]
        ):
            continue
        if relationship.uselist:
            assert relationship.lazy == "raise", (
                f"Relationship '{relationship.key}' on model '{model.__name__}' "
                f"is set to lazy='{relationship.lazy}'. It must be set to 'raise'."
            )
