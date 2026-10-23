from importlib.metadata import EntryPoint, entry_points

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.database import database
from app.plugins import registry
from app.settings import settings

name = "test_app"

FAKE_PLATFORMS = {
    "cloud": "tests.fixtures.fake_plugin.schema:FakeCloudPlatform",
    "fake-link": "tests.fixtures.fake_plugin.schema:FakeLinkPlatform",
}


def _entry_points_with_fakes(group: str) -> list[EntryPoint]:
    return [
        *entry_points(group=group),
        *(
            EntryPoint(name=platform, value=value, group=group)
            for platform, value in FAKE_PLATFORMS.items()
        ),
    ]


registry.entry_points = _entry_points_with_fakes  # type: ignore[assignment]
settings.ENABLED_PLUGINS = ["FakeTechnicalAssetConfiguration", "FakeLinkPlugin"]

engine = create_engine(database.get_url())
session_factory = sessionmaker(autoflush=False, bind=engine, query_cls=database.MyQuery)
TestingSessionLocal = scoped_session(session_factory)

test_session = TestingSessionLocal()
