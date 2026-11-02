import pytest
from sqlalchemy import Table, inspect

from app.database.database import Base
from tests import engine

models = [mapper.class_ for mapper in Base.registry.mappers]
association_relationships = [
    relationship
    for mapper in Base.registry.mappers
    for relationship in mapper.relationships
    if isinstance(relationship.secondary, Table)
]
association_tables = {
    relationship.secondary for relationship in association_relationships
}

# The purpose of this list is to ensure we don't have to fix everything all at once
# We can ignore our tech debt for now and improve it later, but we won't make it worse
ignore_list = {
    "TechnicalAsset": ["tags", "access_modes"],
    "Platform": ["services"],
    "User": ["dataset_roles"],
    "OutputPort": ["tags", "access_modes"],
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


@pytest.mark.parametrize(
    "table", sorted(association_tables, key=lambda t: t.name), ids=lambda t: t.name
)
def test_association_table_foreign_keys_declare_ondelete(table):
    migrated = _migrated_ondelete(table.name)
    for foreign_key in table.foreign_keys:
        assert foreign_key.ondelete is not None, (
            f"Foreign key '{table.name}.{foreign_key.parent.name}' must declare "
            "ondelete, e.g. 'CASCADE' or 'NO ACTION'."
        )
        assert migrated[foreign_key.parent.name] == foreign_key.ondelete, (
            f"Foreign key '{table.name}.{foreign_key.parent.name}' declares "
            f"ondelete='{foreign_key.ondelete}', but the migrated database has "
            f"'{migrated[foreign_key.parent.name]}'. Add a migration."
        )


@pytest.mark.parametrize("relationship", association_relationships, ids=str)
def test_association_relationships_use_passive_deletes(relationship):
    assert relationship.passive_deletes, (
        f"Relationship '{relationship}' uses an association table, so it must set "
        "passive_deletes and leave the cleanup to the database."
    )
    parent_columns = [
        foreign_key.parent.name
        for foreign_key in relationship.secondary.foreign_keys
        if foreign_key.column.table is relationship.parent.local_table
    ]
    migrated = _migrated_ondelete(relationship.secondary.name)
    assert [migrated[column] for column in parent_columns] == ["CASCADE"], (
        f"Relationship '{relationship}' leaves the cleanup to the database, so "
        f"{relationship.secondary.name}.{parent_columns} must cascade on delete."
    )


def _migrated_ondelete(table_name: str) -> dict[str, str]:
    return {
        foreign_key["constrained_columns"][0]: foreign_key["options"].get(
            "ondelete", "NO ACTION"
        )
        for foreign_key in inspect(engine).get_foreign_keys(table_name)
    }
