import os
from hashlib import sha256
from pathlib import Path

# Every checkout, and every pytest-xdist worker within it, gets its own test database,
# so parallel runs never truncate or migrate each other's data.
checkout = sha256(str(Path(__file__).resolve().parent).encode()).hexdigest()[:8]
worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
os.environ["POSTGRES_DB"] = f"{os.environ['POSTGRES_DB']}_{checkout}_{worker}"

from importlib.metadata import EntryPoint, entry_points

from sqlalchemy import Connection, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.database import database
from app.plugins import registry
from app.settings import settings

name = "test_app"

FAKE_PLUGINS = {
    "FakeTechnicalAssetConfiguration": "tests.fixtures.fake_plugin.schema:FakeTechnicalAssetConfiguration",
    "SizingTechnicalAssetConfiguration": "tests.fixtures.sizing_plugin.schema:SizingTechnicalAssetConfiguration",
    "FakeLinkPlugin": "tests.fixtures.fake_plugin.schema:FakeLinkPlugin",
}


def _entry_points_with_fakes(group: str) -> list[EntryPoint]:
    return [
        *entry_points(group=group),
        *(
            EntryPoint(name=plugin, value=value, group=group)
            for plugin, value in FAKE_PLUGINS.items()
        ),
    ]


registry.entry_points = _entry_points_with_fakes  # type: ignore[assignment]
settings.ENABLED_PLUGINS = list(FAKE_PLUGINS)
settings.POSTHOG_ENABLED = False


class RollbackSession(Session):
    """Runs every session inside the transaction a test rolls back afterwards.

    The `clear_db` fixture opens one connection per test, begins a transaction
    on it and stores it in `rollback_connection`. While it is set, every
    session asks for that connection instead of a fresh one from the engine,
    so factories, requests through the TestClient, background tasks and the
    Casbin adapter all read and write inside that single transaction. After
    the test the fixture rolls it back, which is much cheaper than truncating
    every table. Outside a test, or in a test marked `commits`, it is None and
    sessions fall back to the engine as usual.

    The connection is looked up in `get_bind` rather than passed as `bind` to
    the sessionmaker, because some sessions outlive a single test: the
    `test_session` the factories share is created once at import, and the
    scoped sessions of the TestClient's worker threads are reused across
    tests. `get_bind` runs whenever a session needs a connection, so those
    sessions also join the current test's transaction.
    """

    rollback_connection: Connection | None = None

    def get_bind(self, *args, **kwargs):
        return RollbackSession.rollback_connection or super().get_bind(*args, **kwargs)


def rollback_sessionmaker(**kwargs) -> sessionmaker:
    # With create_savepoint, a session joining the test's transaction works in a
    # SAVEPOINT: its commit() releases the savepoint and its rollback() only
    # undoes its own work, so the code under test behaves as it does against a
    # real database while the outer transaction stays open until the test ends.
    return sessionmaker(
        class_=RollbackSession, join_transaction_mode="create_savepoint", **kwargs
    )


engine = create_engine(database.get_url())
session_factory = rollback_sessionmaker(
    autoflush=False, bind=engine, query_cls=database.MyQuery
)
# The app opens its own sessions through SessionLocal, e.g. get_system_db_session
# and the background tasks. Modules import it by name, so it is changed in place
# rather than replaced, to reach the reference they already hold.
database.SessionLocal.class_ = RollbackSession
database.SessionLocal.configure(join_transaction_mode="create_savepoint")
TestingSessionLocal = scoped_session(session_factory)

test_session = TestingSessionLocal()
