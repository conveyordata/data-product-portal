import os
from hashlib import sha256
from pathlib import Path

checkout = sha256(str(Path(__file__).resolve().parent).encode()).hexdigest()[:8]
os.environ["POSTGRES_DB"] = f"{os.environ['POSTGRES_DB']}_{checkout}"

from importlib.metadata import EntryPoint, entry_points

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

engine = create_engine(database.get_url())
session_factory = sessionmaker(autoflush=False, bind=engine, query_cls=database.MyQuery)
TestingSessionLocal = scoped_session(session_factory)

test_session = TestingSessionLocal()
