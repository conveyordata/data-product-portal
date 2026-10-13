from importlib import import_module

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import select

from app.data_products.model import DataProductEnvironment
from tests.factories import DataProductFactory, DomainFactory, EnvironmentFactory

migration = import_module(
    "app.database.alembic.versions.2026_10_12_1100-d7b8c9e0f123_data_product_environments"
)


def test_upgrade__snapshots_domain_and_global_environments(session):
    global_environment = EnvironmentFactory(name="dev", is_global=True)
    domain_environment = EnvironmentFactory(name="prd", is_global=False)
    EnvironmentFactory(name="acc", is_global=False)
    domain = DomainFactory(environments=[domain_environment])
    first = DataProductFactory(domain=domain)
    second = DataProductFactory(domain=domain)
    fallback = DataProductFactory()

    with session.begin_nested() as savepoint:
        with Operations.context(MigrationContext.configure(session.connection())):
            migration.downgrade()
            migration.upgrade()
        rows = session.execute(
            select(
                DataProductEnvironment.data_product_id,
                DataProductEnvironment.environment_id,
                DataProductEnvironment.creation_date,
            )
        ).all()
        assert {
            (str(row.data_product_id), str(row.environment_id)) for row in rows
        } == {
            (str(first.id), str(domain_environment.id)),
            (str(second.id), str(domain_environment.id)),
            (str(fallback.id), str(global_environment.id)),
        }
        assert all(row.creation_date is not None for row in rows)
        savepoint.rollback()


def test_upgrade__rejects_products_without_any_environments(session):
    DataProductFactory()
    with session.begin_nested() as savepoint:
        with Operations.context(MigrationContext.configure(session.connection())):
            migration.downgrade()
            with pytest.raises(
                RuntimeError, match="Configure global or Domain environments"
            ):
                migration.upgrade()
        savepoint.rollback()
